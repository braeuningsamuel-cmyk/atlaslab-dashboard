/* Bootstreep Homelab Dashboard frontend logic.
 * Pure vanilla JS — no build step required, works in any browser.
 */

const fmtBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    if (!bytes && bytes !== 0) return '-';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let v = bytes, i = 0;
    while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
    return v.toFixed(1) + ' ' + units[i];
};

const fmtDuration = (sec) => {
    if (!sec && sec !== 0) return '-';
    const d = Math.floor(sec / 86400);
    const h = Math.floor((sec % 86400) / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return (d > 0 ? d + 'd ' : '') + (h > 0 ? h + 'h ' : '') + m + 'm';
};

const setBar = (id, percent) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.width = Math.max(0, Math.min(100, percent)) + '%';
    el.className = 'bar-fill ' + (percent >= 90 ? 'danger' : percent >= 70 ? 'warn' : 'ok');
};

const setText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
};

const escapeHtml = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

async function loadSystemStats() {
    try {
        const resp = await fetch('/api/system_stats');
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        setText('cpu-usage', data.cpu_percent.toFixed(1) + '%');
        setBar('cpu-bar', data.cpu_percent);
        setText('cpu-detail', `${data.cpu_count || '?'} cores · load ${data.load_avg.map(x => x.toFixed(2)).join(' / ')}`);

        setText('mem-usage', data.mem_percent.toFixed(1) + '%');
        setBar('mem-bar', data.mem_percent);
        setText('mem-detail', `${fmtBytes(data.mem_used)} / ${fmtBytes(data.mem_total)}`);

        setText('disk-usage', data.disk_percent.toFixed(1) + '%');
        setBar('disk-bar', data.disk_percent);
        setText('disk-detail', `${fmtBytes(data.disk_used)} / ${fmtBytes(data.disk_total)}`);

        const totalNet = (data.net_bytes_sent || 0) + (data.net_bytes_recv || 0);
        setText('net-usage', fmtBytes(totalNet));
        setText('net-detail', `↑ ${fmtBytes(data.net_bytes_sent)}  ↓ ${fmtBytes(data.net_bytes_recv)}`);

        setText('uptime', fmtDuration(data.uptime_seconds));
        setText('boot-time', 'seit ' + data.boot_time);

        setText('platform-info', data.platform + ' ' + data.platform_release);
        setText('arch-info', `${data.architecture} · Python ${data.python_version}`);
        setText('host-info', data.hostname);
    } catch (err) {
        console.error('System stats error:', err);
        setText('cpu-usage', 'Fehler');
        setText('mem-usage', 'Fehler');
        setText('disk-usage', 'Fehler');
    }
}

async function loadRepos() {
    const list = document.getElementById('repo-list');
    try {
        const resp = await fetch('/api/repos');
        const data = await resp.json();

        list.innerHTML = '';
        if (!Array.isArray(data) || data.length === 0) {
            list.innerHTML = '<p class="muted">Keine Repositories gefunden.</p>';
            setText('repo-summary', '0 Repos');
            return;
        }

        let upToDate = 0, behind = 0, errored = 0;
        data.forEach(repo => {
            const card = document.createElement('div');
            let cls = 'repo-card';
            let badge = '<span class="repo-badge ok">Up to date</span>';
            if (repo.error) {
                cls += ' error';
                badge = `<span class="repo-badge error" title="${escapeHtml(repo.error)}">Fehler</span>`;
                errored++;
            } else if (repo.behind) {
                cls += ' behind';
                badge = `<span class="repo-badge behind">Behind ${repo.behind_count}</span>`;
                behind++;
            } else if (repo.ahead > 0) {
                cls += ' ahead';
                badge = `<span class="repo-badge ahead">Ahead ${repo.ahead}</span>`;
            } else {
                upToDate++;
            }
            card.className = cls;

            card.innerHTML = `
                <div class="repo-name">${escapeHtml(repo.name)}</div>
                <div class="repo-commit" title="${escapeHtml(repo.last_commit || '')}">${escapeHtml(repo.last_commit || '(kein Commit)')}</div>
                <div class="repo-meta">
                    <span class="repo-branch">${escapeHtml(repo.branch || '?')}</span>
                    <span>${escapeHtml(repo.last_commit_date || '')}</span>
                    ${badge}
                </div>
            `;
            list.appendChild(card);
        });

        setText('repo-summary', `${data.length} Repos · ${upToDate} ok, ${behind} behind, ${errored} errors`);
    } catch (err) {
        console.error('Repos error:', err);
        list.innerHTML = `<p class="muted">Fehler beim Laden: ${escapeHtml(err.message)}</p>`;
    }
}

async function loadQuality() {
    const list = document.getElementById('quality-list');
    try {
        const resp = await fetch('/api/repos');
        const data = await resp.json();
        list.innerHTML = '';

        data.forEach(repo => {
            if (repo.error) return;
            const q = repo.quality_bar || {};
            const card = document.createElement('div');
            card.className = 'quality-card';
            const score = repo.quality_score;
            const max = repo.quality_max || 5;
            let scoreClass = 'bad';
            if (score >= max) scoreClass = 'good';
            else if (score >= 3) scoreClass = 'partial';

            const item = (ok, label) => `<span class="q-item ${ok ? 'ok' : 'miss'}">${ok ? '✓' : '✗'} ${label}</span>`;
            card.innerHTML = `
                <div class="quality-card-head">
                    <span class="quality-name">${escapeHtml(repo.name)}</span>
                    <span class="quality-score ${scoreClass}">${score}/${max}</span>
                </div>
                <div class="quality-items">
                    ${item(q.makefile, 'Makefile')}
                    ${item(q.architecture, 'ARCHITECTURE.md')}
                    ${item(q.env_example, '.env.example')}
                    ${item(q.ci, `CI (${(q.ci_files || []).length})`)}
                    ${item((q.docker_files || []).length > 0, `Docker (${(q.docker_files || []).length})`)}
                </div>
            `;
            list.appendChild(card);
        });

        if (list.children.length === 0) {
            list.innerHTML = '<p class="muted">Keine Repositories zur Anzeige.</p>';
        }
    } catch (err) {
        list.innerHTML = `<p class="muted">Fehler: ${escapeHtml(err.message)}</p>`;
    }
}

let refreshInFlight = false;

async function refreshAll() {
    if (refreshInFlight) return;  // guard against overlapping refresh + setInterval
    const btn = document.getElementById('refresh-btn');
    refreshInFlight = true;
    if (btn) { btn.disabled = true; btn.textContent = '… lädt'; }
    try {
        await Promise.all([loadSystemStats(), loadRepos(), loadQuality()]);
        setText('last-refresh', 'aktualisiert ' + new Date().toLocaleTimeString('de-DE'));
    } catch (err) {
        console.error('refreshAll failed:', err);
    } finally {
        refreshInFlight = false;
        if (btn) { btn.disabled = false; btn.innerHTML = '&#x21bb; Aktualisieren'; }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
    setInterval(refreshAll, 60000); // auto-refresh every 60s
    const btn = document.getElementById('refresh-btn');
    if (btn) btn.addEventListener('click', refreshAll);
});