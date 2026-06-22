# REPO METADATA — manual paste into GitHub Web UI

This file lists the **Description** and **Topics** that should be set on each
of the five Bootstreep repositories.

Because the GitHub personal-access token was compromised earlier in this
session, these values **cannot be set via API**. Paste them manually:

1. Open https://github.com/braeuningsamuel-cmyk/<repo>
2. Click the gear icon ⚙ next to "About" on the right sidebar
3. Paste the **Description** into the description field
4. Paste the **Topics** (comma-separated) into the topics field
5. Click "Save changes"

---

## 1. `bootstreep-homelab`

- URL: https://github.com/braeuningsamuel-cmyk/bootstreep-homelab
- **Description**:

> Privacy-first homelab bootstrap: one command deploys 30+ self-hosted services with hardened Docker, Traefik, Prometheus, and AI agent control.

- **Topics** (10):
```
homelab, self-hosted, docker, bootstrap, traefik, ai-agent, infrastructure, privacy, automation, ansible
```

> NOTE: This description/topics may already be set from an earlier API call.
> Check the repo page; if it matches, do nothing.

---

## 2. `bootstreep-dashboard`

- URL: https://github.com/braeuningsamuel-cmyk/bootstreep-dashboard
- **Description**:

> Cross-platform web dashboard for homelab monitoring — Flask backend + vanilla JS frontend, runs anywhere Python 3.11+ and a browser are available. Replaces the legacy Tauri 2.x desktop shell.

- **Topics** (8):
```
dashboard, flask, python, tauri, homelab, webapp, monitoring, vanilla-js
```

---

## 3. `Homelab-Base`

- URL: https://github.com/braeuningsamuel-cmyk/Homelab-Base
- **Description**:

> Monorepo consolidating the Bootstreep homelab stack: infrastructure automation, Tauri desktop dashboard, TanStack React/Vite guardian app, and meta documentation.

- **Topics** (8):
```
homelab, monorepo, infrastructure, docker-compose, ai-agent, tauri, react, documentation
```

---

## 4. `braeuningsamuel-cmyk`

- URL: https://github.com/braeuningsamuel-cmyk/braeuningsamuel-cmyk
- **Description**:

> Samuel's GitHub profile README — Homelab enthusiast, AI automation builder, privacy-first infrastructure. See the Bootstreep project family for the actual code.

- **Topics** (5):
```
profile, homelab, ai-automation, privacy, portfolio
```

---

## 5. `home-lab-guardian`

- URL: https://github.com/braeuningsamuel-cmyk/home-lab-guardian
- **Description**:

> Atlas.Lab — modern homelab monitoring web app built with TanStack Start, React 19, Vite 7, and Bun. Browser-first, file-based routing, type-safe.

- **Topics** (8):
```
homelab, dashboard, react, vite, tanstack-start, typescript, bun, monitoring
```

---

## Verification

After applying, the local dashboard at http://localhost:5000 should reflect
the descriptions in the repo cards. (The dashboard does not display
description text currently — it shows branch, last commit, and Quality Bar
score. Topics would only show if the backend reads them; it doesn't.)

---

## ⚠️ Security note

The GitHub personal-access token used in this session is **compromised** and
returns `401 Bad credentials` on the GitHub API. Rotate it at
https://github.com/settings/tokens before any further API use.