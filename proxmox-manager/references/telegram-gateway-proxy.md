# Telegram Gateway Proxy via Proxmox Host Xray

## Problem
Hermes Telegram gateway cannot connect to Telegram API from Iran due to internet restrictions. The Proxmox host (192.168.1.10) runs Xray proxy to bypass restrictions.

## Xray Configuration on Proxmox Host
- **Config file**: `/usr/local/etc/xray/config.json` (or `/etc/xray/config.json`)
- **Inbound proxy**: Port **10808** (SOCKS/HTTP mixed, `auth: "noauth"`)
- **NOT port 3128** — that's `spiceproxy` (Proxmox SPICE proxy), requires auth

```json
{
  "inbounds": [
    {
      "tag": "socks",
      "port": 10808,
      "listen": "0.0.0.0",
      "protocol": "mixed",
      "settings": { "auth": "noauth", "udp": true }
    }
  ]
}
```

## Hermes Gateway Configuration
Set `TELEGRAM_PROXY` in `/root/.hermes/.env`:

```bash
TELEGRAM_PROXY=socks5://192.168.1.10:10808
```

The gateway auto-detects proxy from env vars (see `gateway/platforms/base.py::resolve_proxy_url`):
1. Platform-specific: `TELEGRAM_PROXY`
2. Generic: `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY` (and lowercase)
3. macOS system proxy (auto-detect)

## Required Steps
1. Install `python-telegram-bot` in Hermes venv:
   ```bash
   /usr/local/lib/hermes-agent/venv/bin/pip install python-telegram-bot
   ```
2. Set `TELEGRAM_PROXY` in `.env` (user must edit manually — file is protected)
3. Restart gateway:
   ```bash
   systemctl restart hermes-gateway
   ```

## Verification
- Check gateway status: `hermes gateway status`
- Check gateway state: `cat ~/.hermes/gateway_state.json`
- Look for: `"platforms": {"telegram": {"state": "connected"}}`
- Logs: `hermes logs --since 10m | grep -i telegram`

## Troubleshooting
- **401 invalid ticket**: Wrong port (using 3128 instead of 10808) or auth required
- **Connection timeout**: Proxy not reachable, wrong IP/port, or firewall
- **python-telegram-bot not installed**: Install in Hermes venv (not system Python)
- **.env protected**: Use `sed` or manual edit, not agent write_file/patch