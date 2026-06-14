<p align="center">
  <img src="https://raw.githubusercontent.com/braeuningsamuel-cmyk/bootstreep-dashboard/main/src-tauri/icons/icon.png" width="100" alt="Bootstreep Logo">
</p>

<h1 align="center">Bootstreep Dashboard</h1>

<p align="center">
  <strong>Homelab Server Management — Desktop App</strong><br>
  <sub>Tauri 2.x · Rust Backend · Vanilla Frontend · ~2 MB</sub>
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#development">Development</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#homelab">Homelab</a> ·
  <a href="#license">License</a>
</p>

---

## Features

| Category | Capabilities |
|----------|-------------|
| **Dashboard** | Real-time CPU, RAM, Network sparklines · Docker container overview · Uptime |
| **Docker** | Container lifecycle (start/stop/restart) · Logs · Exec · Live stats |
| **Services** | systemd service management · Start/stop/enable/disable |
| **Terminal** | Full PTY terminal with output streaming · Command history |
| **Files** | File browser · Editor · Create/delete/rename |
| **Network** | Interfaces · Routes · DNS · Firewall (UFW) |
| **Storage** | Disk usage · Mount points · SMART info |
| **Processes** | Top processes by CPU/RAM · Kill |
| **Crontab** | Cron job editor |
| **Packages** | apt/dnf/pacman updates · Install/remove |
| **Users** | System users overview |
| **Homelab** | WireGuard · Jellyfin · Arr-Stack · Ollama · Syncthing · Uptime Kuma · Nextcloud OCC |
| **Profiles** | Multi-server management · SSH remote · Profile switching |
| **Settings** | Theme toggle (Dark/Light/System) · Connection config |
| **Ports** | Port check for 21 homelab services |
| **Power** | Reboot / Shutdown |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Desktop Framework** | [Tauri 2.x](https://tauri.app) (~2 MB binary) |
| **Backend** | Rust (sysinfo, tokio, portable-pty) |
| **Frontend** | Vanilla HTML/CSS/JS (no framework, no build step) |
| **SSH** | OpenSSH CLI (password-less key auth) |
| **Theme** | Bootstreep Dark (#09090b / #6366f1 / #10b981) |

## Screenshots

> Dashboard: Echtzeit CPU/RAM/Disk � Docker Control � Pi-hole DNS � Terminal � Multi-Profil

## Installation

### Download

Download the latest release from [GitHub Releases](https://github.com/braeuningsamuel-cmyk/bootstreep-dashboard/releases):

- **Windows**: `Bootstreep_2.5.0_x64-setup.exe` (~2 MB)
- **Windows MSI**: `Bootstreep_2.5.0_x64_en-US.msi` (~3 MB)

### Build from Source

**Prerequisites:**
- [Node.js](https://nodejs.org) 20+
- [Rust](https://rustup.rs) (MSVC toolchain on Windows)
- WebView2 Runtime (Windows 10/11)

```bash
git clone https://github.com/braeuningsamuel-cmyk/bootstreep-dashboard.git
cd bootstreep-dashboard
npm install
npm run tauri build
```

Output: `src-tauri/target/release/bundle/nsis/Bootstreep_*_x64-setup.exe`

## Development

```bash
# Start dev server with hot reload
npm run tauri dev

# Production build
npm run tauri build

# Debug build (with DevTools)
npm run tauri build --debug

# Rust checks
npm run check       # Type check
npm run clippy      # Lint
npm run fmt         # Format
```

### VS Code

Open the project in VS Code — extensions are auto-suggested via `.vscode/extensions.json`.

| Shortcut | Action |
|----------|--------|
| `F5` | Full Stack Debug (Rust + Chrome) |
| `Ctrl+Shift+P` → Tasks | tauri:dev, tauri:build, cargo:check, cargo:clippy |

## Architecture

```
bootstreep-dashboard/
├── src/                          # Frontend (Vanilla JS)
│   ├── index.html                # Single-file SPA (~2000 lines)
│   └── main.js                   # App logic (~900 lines)
│
├── src-tauri/                    # Rust Backend
│   ├── src/
│   │   ├── lib.rs                # 46 Tauri commands (~1600 lines)
│   │   └── main.rs               # Entry point
│   ├── Cargo.toml                # Rust dependencies
│   ├── tauri.conf.json           # Tauri config
│   ├── capabilities/             # Tauri 2.x permission system
│   │   └── default.json
│   └── permissions/              # 46 permission definitions
│       ├── allow-*.json
│       └── shell-scope-homelab.json
│
├── .vscode/                      # VS Code config
│   ├── launch.json               # Debug configs
│   ├── tasks.json                # Build tasks
│   ├── settings.json             # Editor settings
│   └── extensions.json           # Recommended extensions
│
├── .github/workflows/
│   └── release.yml               # CI: Build + Release (Windows/Linux/Android)
│
├── package.json                  # Node.js config
└── README.md
```

### Commands Overview (46 total)

| Command | Description |
|---------|-------------|
| `system_stats` | CPU, RAM, disk, network, uptime |
| `docker_list` | List Docker containers |
| `docker_action` | Start/stop/restart container |
| `docker_logs` | Container logs |
| `docker_exec` | Execute command in container |
| `docker_stats` | Live Docker stats |
| `service_list` | List systemd services |
| `service_action` | Start/stop/restart service |
| `run_command` | Execute shell command |
| `file_list/read/write/delete/mkdir/rename` | File operations |
| `network_info` | Network interfaces, routes, DNS |
| `firewall_status/action` | UFW firewall management |
| `storage_info` | Disk usage and mounts |
| `process_list/kill` | Process management |
| `crontab_list/save` | Cron job management |
| `package_updates/action` | Package manager operations |
| `user_list` | System users |
| `check_ports` | Port availability check |
| `system_power` | Reboot/shutdown |
| `set_connection/get_connection` | SSH connection config |
| `test_ssh_connection` | Test SSH connectivity |
| `allow_pty_spawn/write/resize/close` | PTY terminal |
| `allow_wireguard_peers` | WireGuard VPN peers |
| `allow_jellyfin_control` | Jellyfin media server |
| `allow_arr_stack` | Sonarr/Radarr/Lidarr |
| `allow_ollama_models` | Ollama LLM models |
| `allow_syncthing_folders` | Syncthing file sync |
| `allow_uptime_kuma` | Uptime monitoring |
| `allow_nextcloud_occ` | Nextcloud CLI |
| `profile_list/add/remove/switch/get_active` | Server profiles |

## Homelab

Bootstreep Dashboard is designed for Ubuntu Server 24.04 homelabs with Docker.

### Port Mapping

| Port | Service |
|------|---------|
| 22 | SSH |
| 53 | Pi-hole DNS |
| 80/443 | HTTP/HTTPS (Caddy) |
| 3000 | Hermes (AI) |
| 3001 | Uptime Kuma |
| 445 | Samba |
| 51820 | WireGuard VPN |
| 8080 | Websurfx |
| 8081 | Pi-hole Web |
| 8082/9443 | Nextcloud AIO |
| 8087 | AMP (Minecraft) |
| 8096 | Jellyfin |
| 8384 | Syncthing |
| 8989/7878/9696/6767 | Arr Stack |
| 9050 | Tor |
| 11434 | Ollama (AI) |

### SSH Remote

1. Enter Server IP and User in the topbar
2. Click "Verbinden" (SSH key auth required)
3. App switches to Remote mode (purple badge)
4. All commands execute on the remote server

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with Tauri 2.x · Rust · Vanilla JS</sub><br>
  <sub>Bootstreep Dashboard v2.5.0</sub>
</p>

