# Docker — one-time setup

If `docker --version` fails, install Docker once. See [`docker.md`](docker.md) for credentials, tags, and build/push commands.

**macOS:** Download Docker Desktop from https://docs.docker.com/desktop/setup/install/mac-install/
- Choose the **Apple Silicon** installer for M-series Macs, or **Intel Chip** for older Macs
- Open the DMG, drag Docker to Applications, and launch it

**Windows:** Download Docker Desktop from https://docs.docker.com/desktop/setup/install/windows-install/
- WSL 2 is necessary. If absent, run `wsl --install` in an administrator PowerShell. Then, restart. Docker Desktop detects WSL 2 automatically
- After installation, use `docker` commands in the WSL2 terminal without additional configuration
- Run the installer and follow the setup wizard

**Linux:** See https://docs.docker.com/engine/install/ for instructions for your distribution

```bash
# Linux convenience script (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # allow non-root usage (re-login after)
```
