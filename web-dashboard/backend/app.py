"""Bootstreep Homelab Web Dashboard backend.

Provides:
- /api/system_stats  -> host CPU/mem/disk/network info via psutil
- /api/repos         -> per-repo status + quality-bar checks via GitPython
- /api/repos/<name>/fetch -> trigger a git fetch for a single repo
- /api/health        -> simple liveness probe
- /                  -> serve the frontend HTML

Runs on any OS with Python 3.8+ and the deps installed in the venv.
"""
from flask import Flask, jsonify, render_template
import psutil
import platform
import os
import git
from datetime import datetime, timezone

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')

REPOS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repos'))


def get_default_branch(repo):
    """Resolve the default branch from origin/HEAD, falling back to main/master."""
    try:
        names = [r.name for r in repo.remotes.origin.refs]
        if 'origin/HEAD' in names:
            head_ref = next(r for r in repo.remotes.origin.refs if r.name == 'HEAD')
            return head_ref.reference.name.split('/')[-1]
    except Exception:
        pass
    names = [r.name for r in repo.remotes.origin.refs]
    if 'origin/main' in names:
        return 'main'
    if 'origin/master' in names:
        return 'master'
    return repo.active_branch.name


def get_local_branch(repo, default_branch):
    """Make sure the default branch is checked out locally."""
    local_branches = [b.name for b in repo.branches]
    if default_branch in local_branches:
        return default_branch
    try:
        repo.git.checkout('-B', default_branch, f'origin/{default_branch}')
        return default_branch
    except Exception:
        return repo.active_branch.name


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/system_stats')
def system_stats():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = psutil.boot_time()
        boot_time_str = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        net = psutil.net_io_counters()
        try:
            load_avg = psutil.getloadavg()
        except (AttributeError, OSError):
            load_avg = (0.0, 0.0, 0.0)
        stats = {
            'cpu_percent': cpu_percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'load_avg': list(load_avg),
            'mem_percent': mem.percent,
            'mem_used': mem.used,
            'mem_total': mem.total,
            'disk_percent': disk.percent,
            'disk_used': disk.used,
            'disk_total': disk.total,
            'net_bytes_sent': net.bytes_sent,
            'net_bytes_recv': net.bytes_recv,
            'boot_time': boot_time_str,
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'uptime_seconds': int(datetime.now().timestamp() - boot_time),
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def detect_stack(repo_path):
    """Detect project stack from files in the repo root + first-level dirs.

    Returns one of:
      'cli'      -> Makefile + Ansible/Bash + Docker Compose (bootstreep-homelab)
      'tauri'    -> Tauri desktop app (Rust + web frontend)
      'react'    -> React/Vite/TanStack web app
      'monorepo' -> contains multiple subprojects
      'profile'  -> GitHub profile README-only
    """
    has_makefile = os.path.isfile(os.path.join(repo_path, 'Makefile'))
    has_cargo = os.path.isfile(os.path.join(repo_path, 'src-tauri', 'Cargo.toml'))
    has_package_json = os.path.isfile(os.path.join(repo_path, 'package.json'))
    has_compose = (
        os.path.isfile(os.path.join(repo_path, 'docker-compose.yml'))
        or os.path.isfile(os.path.join(repo_path, 'docker-compose.yaml'))
        or any(os.path.isfile(os.path.join(repo_path, 'compose', f))
               for f in ('docker-compose.yml', 'docker-compose.yaml', 'alloy', 'authentik'))
    )
    has_bootstrap = os.path.isdir(os.path.join(repo_path, 'bootstrap'))
    has_ansible = os.path.isdir(os.path.join(repo_path, 'ansible'))
    has_infra = os.path.isdir(os.path.join(repo_path, 'infra'))
    has_apps = os.path.isdir(os.path.join(repo_path, 'apps'))

    if has_makefile and (has_compose or has_bootstrap or has_ansible):
        return 'cli'
    if has_cargo and has_package_json:
        return 'tauri'
    if has_package_json and not has_makefile:
        return 'react'
    if has_infra and has_apps:
        return 'monorepo'
    return 'profile'


def _file_min_size(path, min_bytes):
    """Return True only if path exists AND has at least min_bytes of content."""
    try:
        return os.path.isfile(path) and os.path.getsize(path) >= min_bytes
    except OSError:
        return False


def quality_bar_for_stack(repo_path, stack):
    """Return stack-appropriate quality-bar checks (always 5 criteria).

    CLI/tauri/monorepo  -> Makefile / ARCHITECTURE.md / .env.example / CI / Dockerfiles
    React/Vite          -> package.json (with scripts) / tsconfig.json / README.md / CI / lint config
    Profile             -> README.md / GitHub topics / social badges / repo description / pinned repos
    """
    # ARCHITECTURE.md must be substantive — reject placeholder/TODO content
    arch_path = os.path.join(repo_path, 'ARCHITECTURE.md')
    has_architecture = _file_min_size(arch_path, 500)
    readme_path = os.path.join(repo_path, 'README.md')
    has_readme = _file_min_size(readme_path, 200)
    has_makefile = os.path.isfile(os.path.join(repo_path, 'Makefile'))
    has_env_example = os.path.isfile(os.path.join(repo_path, '.env.example'))
    ci_dir = os.path.join(repo_path, '.github', 'workflows')
    has_ci_files = []
    if os.path.isdir(ci_dir):
        for f in os.listdir(ci_dir):
            if f.endswith(('.yml', '.yaml')):
                has_ci_files.append(f)
    has_ci = len(has_ci_files) > 0

    has_package_json = os.path.isfile(os.path.join(repo_path, 'package.json'))
    has_tsconfig = os.path.isfile(os.path.join(repo_path, 'tsconfig.json'))
    has_readme = os.path.isfile(os.path.join(repo_path, 'README.md'))
    has_lint = (
        os.path.isfile(os.path.join(repo_path, 'eslint.config.js'))
        or os.path.isfile(os.path.join(repo_path, '.eslintrc.json'))
        or os.path.isfile(os.path.join(repo_path, '.eslintrc.js'))
    )
    has_bats = 0
    docker_files = []
    pkg_scripts_ok = False
    if has_package_json:
        try:
            import json as _json
            with open(os.path.join(repo_path, 'package.json'), encoding='utf-8') as fp:
                pkg = _json.load(fp)
                scripts = pkg.get('scripts') or {}
                pkg_scripts_ok = bool(scripts.get('build') and scripts.get('lint'))
        except Exception:
            pass
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.output', '.tanstack')]
        for f in files:
                            if f.endswith('.bats'):
                                has_bats += 1
                            if (f.startswith('docker-compose') and (f.endswith('.yml') or f.endswith('.yaml'))) \
                                    or f == 'Dockerfile' or f.endswith('.dockerfile'):
                                docker_files.append(os.path.relpath(os.path.join(root, f), repo_path))

    if stack == 'react':
        # React/Vite apps don't ship Docker; 5 criteria on JS-toolchain maturity.
        return {
            'stack': 'react',
            'criteria': {
                'package_json': has_package_json,
                'package_json_scripts_ok': pkg_scripts_ok,
                'tsconfig': has_tsconfig,
                'readme': has_readme,
                'lint_config': has_lint,
                'ci': has_ci,
            },
            'score': min(5, sum([
                has_package_json,
                pkg_scripts_ok,
                has_tsconfig,
                has_readme,
                has_lint,
                has_ci,
            ])),
            'max': 5,
            'has_docker': len(docker_files) > 0,
            'note': 'docker_files is bonus, not counted toward score',
        }
    if stack == 'profile':
        return {
            'stack': 'profile',
            'criteria': {
                'readme': has_readme,
                'makefile': has_makefile,
                'architecture': has_architecture,
                'env_example': has_env_example,
                'ci': has_ci,
            },
            'score': sum([
                has_readme,
                has_makefile,
                has_architecture,
                has_env_example,
                has_ci,
            ]),
            'max': 5,
        }
    if stack == 'tauri':
        # Tauri apps don't ship Docker; weight on docs/build/lint instead.
        # 5 criteria, but max=5 means docker_files is bonus not penalty.
        return {
            'stack': 'tauri',
            'criteria': {
                'makefile': has_makefile,
                'architecture': has_architecture,
                'env_example': has_env_example,
                'ci': has_ci,
                'package_json': has_package_json,
            },
            'score': sum([
                has_makefile,
                has_architecture,
                has_env_example,
                has_ci,
                has_package_json,
            ]),
            'max': 5,
            'docker_files': docker_files,
            'has_docker': len(docker_files) > 0,
        }
    # cli + monorepo use the original 5-point bar
    return {
        'stack': stack,
        'criteria': {
            'makefile': has_makefile,
            'architecture': has_architecture,
            'env_example': has_env_example,
            'ci': has_ci,
            'docker_files': len(docker_files) > 0,
        },
        'score': sum([
            has_makefile,
            has_architecture,
            has_env_example,
            has_ci,
            len(docker_files) > 0,
        ]),
        'max': 5,
        'bats_count': has_bats,
        'docker_files': docker_files,
    }


@app.route('/api/repos')
def repo_status():
    repos = []
    if not os.path.exists(REPOS_PATH):
        return jsonify({'error': 'repos directory not found', 'repos': []}), 200

    for repo_name in sorted(os.listdir(REPOS_PATH)):
        repo_path = os.path.join(REPOS_PATH, repo_name)
        git_dir = os.path.join(repo_path, '.git')
        if not os.path.isdir(git_dir):
            repos.append({'name': repo_name, 'error': 'Not a git repository'})
            continue
        try:
            repo = git.Repo(repo_path)
            try:
                repo.remotes.origin.fetch()
            except Exception:
                pass

            default_branch = get_default_branch(repo)
            branch = get_local_branch(repo, default_branch)
            try:
                repo.git.checkout(branch)
            except Exception:
                pass

            last_commit = repo.head.commit
            last_commit_date = last_commit.committed_datetime
            if last_commit_date.tzinfo is None:
                last_commit_date = last_commit_date.replace(tzinfo=timezone.utc)
            last_commit_date_str = last_commit_date.strftime('%Y-%m-%d %H:%M:%S %Z')

            ahead_n = 0
            behind_n = 0
            behind = False
            try:
                remote_commit = repo.remotes.origin.refs[branch].commit
                if last_commit.hexsha != remote_commit.hexsha:
                    ahead_n = len(list(repo.iter_commits(f'{remote_commit.hexsha}..HEAD')))
                    behind_n = len(list(repo.iter_commits(f'HEAD..{remote_commit.hexsha}')))
                    behind = True
            except Exception:
                pass

            ci_dir = os.path.join(repo_path, '.github', 'workflows')
            ci_files = []
            if os.path.isdir(ci_dir):
                for f in os.listdir(ci_dir):
                    if f.endswith(('.yml', '.yaml')):
                        ci_files.append(f)

            stack = detect_stack(repo_path)
            qbar = quality_bar_for_stack(repo_path, stack)

            docker_files = []
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.output', '.tanstack')]
                for f in files:
                    if f in ('docker-compose.yml', 'docker-compose.yaml', 'Dockerfile') or f.endswith('.dockerfile'):
                        docker_files.append(os.path.relpath(os.path.join(root, f), repo_path))

            bats_files = []
            if stack in ('cli', 'monorepo', 'tauri'):
                for root, dirs, files in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.output', '.tanstack')]
                    for f in files:
                        if f.endswith('.bats'):
                            bats_files.append(f)
                qbar['bats_count'] = len(bats_files)

            repos.append({
                'name': repo_name,
                'branch': branch,
                'default_branch': default_branch,
                'stack': stack,
                'last_commit': last_commit.message.strip().split('\n')[0][:120],
                'last_commit_date': last_commit_date_str,
                'behind': behind,
                'ahead': ahead_n,
                'behind_count': behind_n,
                'url': next(iter(repo.remotes.origin.urls), ''),
                'quality_bar': qbar['criteria'],
                'quality_score': qbar['score'],
                'quality_max': qbar['max'],
                'quality_stack': stack,
                'ci_files': ci_files,
                'docker_files': (docker_files if isinstance(docker_files, list) else [])[:10],
                'bats_count': qbar.get('bats_count', 0) if isinstance(qbar.get('bats_count'), int) else 0,
            })
        except Exception as e:
            repos.append({'name': repo_name, 'error': str(e)})

    return jsonify(repos)


@app.route('/api/repos/<name>/fetch', methods=['POST'])
def fetch_repo(name):
    # Path-traversal protection: reject anything that isn't a safe single-segment name
    if not name or '/' in name or '\\' in name or name in ('.', '..'):
        return jsonify({'error': 'invalid repo name'}), 400
    repo_path = os.path.join(REPOS_PATH, name)
    real_repos = os.path.realpath(REPOS_PATH)
    real_target = os.path.realpath(repo_path)
    if not real_target.startswith(real_repos + os.sep) and real_target != real_repos:
        return jsonify({'error': 'repo path escapes REPOS_PATH'}), 400
    git_dir = os.path.join(repo_path, '.git')
    if not os.path.isdir(git_dir):
        return jsonify({'error': 'Not a git repo'}), 404
    try:
        repo = git.Repo(repo_path)
        for remote in repo.remotes:
            remote.fetch()  # no prune=True — keeps refs intact for downstream iteration
        return jsonify({'status': 'fetched', 'repo': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat()})


if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'js'), exist_ok=True)
    repos_count = 0
    if os.path.isdir(REPOS_PATH):
        repos_count = sum(1 for d in os.listdir(REPOS_PATH) if os.path.isdir(os.path.join(REPOS_PATH, d, '.git')))
    print(f'Repos path: {REPOS_PATH}')
    print(f'Repos found: {repos_count}')
    app.run(host='0.0.0.0', port=5000, debug=False)