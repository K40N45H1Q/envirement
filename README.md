# Launcher

`launcher.py` is a simple script for installing dependencies and running the project.

It starts:

- backend
- frontend
- Cloudflare Tunnel, when the `--tun` flag is used

## Requirements

Before using the launcher, install:

- Python 3.13
- Node.js LTS
- npm
- Windows Package Manager (`winget`) — required for automatic `cloudflared` installation on Windows

## Project Structure

The script expects this structure:

```text
project/
├── launcher.py
├── requirements.txt
├── backend/
│   └── run.py
└── frontend/
    └── package.json