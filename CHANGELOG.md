# Changelog

## v2.6.2 (2026-06-15) – Version-Sync & Fixes

### Fixes (CRITICAL)
- **tauri.conf.json**: `$schema` nicedoc/tauri → tauri-apps/tauri (Typosquatting)
- **tauri.conf.json**: Version `2.1.0` → `2.6.2`
- **capabilities/default.json**: `bootstreep:` → `bootstreep-dashboard:` (43 Einträge)
- **lib.rs**: 5 Profile-Commands: Permission-Files + Capabilities hinzugefügt
- **lib.rs**: SSH-Quoting in `docker_exec` verbessert

### Fixes (HIGH)
- **lib.rs**: 18× `.lock().unwrap()` → `.lock().map_err()` (kein Panic bei Mutex-Poisoning)
- **lib.rs**: `.expect("cannot get metadata")` → graceful error handling (skip entry)
- **Cargo.toml**: Version `2.6.1` → `2.6.2`
- **index.html**: Version `v2.1.0` → `v2.6.2` (Sidebar + About)
- **CHANGELOG.md**: v2.6.0, v2.6.1, v2.6.2 Einträge ergänzt

### Fixes (MEDIUM)
- **main.js**: `ptyUnlisten` / `ptySessionId` Deklaration vor Erstnutzung
- **tauri.conf.json**: CSP `connect-src`: `ipc://localhost` entfernt (Tauri 1 Legacy)
- **README.md**: Download-Links `2.5.0` → `2.6.2`
- **README.md**: Footer `v2.6.0` → `v2.6.2`

### Fixes (LOW)
- **lib.rs**: Temp-File-Cleanup in `crontab_save` (PID-basierter Name + Fallback korrigiert)
- **permissions/**: `fs-scope-homelab.json`, `shell-scope-homelab.json`: Unreferenzierte Dateien bereinigt

## v2.5.0 (2026-06-14) – 30-Bug Audit

### Security
- **capabilities**: 44 `bootstreep:allow-*` Berechtigungen hinzugefügt
- **lib.rs**: Signal-Whitelist validierung für `process_kill`

### Fixes
- **index.html**: Fehlende CSS-Klassen hinzugefügt (btn, card-head, etc.)
- **index.html**: Version v2.1.0 → v2.5.0 aktualisiert
- **tauri.conf.json**: `withGlobalTauri: true` + CSP korrigiert
- **README.md**: Placeholder URLs durch echte Repo-Links ersetzt

## v2.4.1 (2026-06-14)

### Fixes
- Bootstreep Rename: Alle Atlas.Lab Referenzen entfernt

## v2.4.0 (2026-06-14)

### Fixes
- Terminal PTY Shell Fallback: `powershell.exe` auf Windows

## v2.3.0 (2026-06-14)

### Fixes
- Speicher Badge Ternary korrigiert (70-90% zeigt jetzt gelb)
- Prozess Memory Display Bug gefixt

## v2.2.0 (2026-06-14)

### Fixes
- Terminal `\n` → `<br>` für Newline Rendering
- `badge-warning` CSS-Klasse hinzugefügt

## v2.1.0 (2026-06-13)

### Features
- Homelab service URL table on the Homelab page (all 22 services with ports and links)
- Extended port check list: +5 ports (3002 Open WebUI, 5678 n8n, 8085 SABnzbd, 8090 Heimdall, 51821 PiVPN)

## v2.0.0 (2026-06-12)

### Features
- Multi-server profile management (add/remove/switch profiles with dropdown)
- Theme toggle: Dark, Light, System (auto-detection)
- Live metrics via Tauri events (real-time CPU/RAM in topbar)
- PTY terminal with full shell session support
- Tauri 2.x migration

### Homelab Integrations
- WireGuard peer management
- Jellyfin media server control
- Arr-Stack (Sonarr/Radarr/Lidarr) status
- Ollama model listing
- Syncthing folder status
- Uptime Kuma monitoring status
- Nextcloud OCC command execution

### Infrastructure
- Event delegation architecture for CSP compliance
- Mobile-responsive design with bottom navigation
- File explorer with editor (read/write server files)
- Process viewer with kill capability
- System power controls (reboot, shutdown)

## v1.0.0 (2026-06-01)

Initial release.
- Basic server dashboard with system stats
- Docker container management (list, start, stop, restart, logs)
- Service management (systemd)
- Network information, firewall control
- Storage monitoring
- Port checking
- Settings page for connection configuration
