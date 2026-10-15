# SSH Access to Proxmox LXC Containers

## Overview
When the Proxmox API `exec` endpoint returns HTTP 501 "Not Implemented" (common on Proxmox VE 8.4+), SSH is the primary alternative for running commands inside containers.

## Common Access Patterns

### 1. Direct SSH to Container IP (Recommended)
```bash
# Find container IP from Proxmox config
python3 scripts/proxmox_api.py config ct <vmid> net0

# SSH directly (requires password or key)
ssh root@<container-ip>
sshpass -p '<password>' ssh root@<container-ip> "command"
```

### 2. SSH via Proxmox Host (if container has no direct network access)
```bash
# From host with shell access
ssh root@<proxmox-host> "pct exec <vmid> -- <command>"
```

### 3. Proxmox Web Console
Use the "Console" tab in Proxmox web UI for interactive access.

## Alpine Linux Containers (Common for Lightweight Templates)

### Service Management (OpenRC, not systemd)
```bash
# Check service status
rc-service sshd status
rc-service <service> status

# Start/stop/restart
rc-service sshd start
rc-service sshd restart

# Enable/disable on boot
rc-update add sshd default
rc-update del sshd default
```

### SSH Config Location
- `/etc/ssh/sshd_config` (main config)
- `/etc/ssh/sshd_config.d/*.conf` (drop-in configs)

### Common SSH Hardening for Alpine
```bash
# Disable password auth (after setting up keys)
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
rc-service sshd restart

# Change default port
sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
rc-service sshd restart
```

## Testing SSH from External Host
```bash
# Install sshpass for password-based automation
apt-get install -y sshpass

# Test connection
sshpass -p '<password>' ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@<container-ip> "echo 'SSH works'"

# Run commands
sshpass -p '<password>' ssh root@<container-ip> "rc-service sshd status"
sshpass -p '<password>' ssh root@<container-ip> "apk add nginx"
```

## Network Configuration Notes
- Container IP is static if configured in Proxmox (`ip=192.168.1.110/24,gw=192.168.1.10`)
- Bridge: typically `vmbr0` on the Proxmox host
- Firewall: Proxmox firewall may be enabled on the container interface (`firewall=1` in net0 config)

## "Failed password" even with correct user/pass (root login blocked)
Symptom: `ssh root@<ct-ip>` fails with `Permission denied (publickey,password)` on your
laptop, yet the container is reachable (sshd running, port 22 open, no PVE firewall rule
blocking it), and `auth.log` shows `Failed password for root from <your-laptop-ip>`.

Root cause: `/etc/ssh/sshd_config` has every relevant directive commented out, so sshd
falls back to its compiled default `PermitRootLogin prohibit-password` — root may log in
with a KEY only, password is refused. This is easy to hit on Ubuntu/Debian LXC templates
where the shipped config leaves these lines commented. (Network, gateway, IP, and the
password were all fine — the auth path was just closed.)

Verify from the host (use `pct exec` since API exec is 501 on PVE 9):
```bash
ssh root@<proxmox-host> "pct exec <vmid> -- sshd -T | grep -iE 'permitrootlogin|passwordauth'"
# expect: permitrootlogin prohibit-password  <- THIS IS THE BUG
```

Fix (apply inside the container, then restart sshd):
```bash
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin yes/;
        s/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
systemctl restart ssh sshd     # Debian/Ubuntu
# rc-service sshd restart      # Alpine (OpenRC)
# verify:
sshd -T | grep -iE 'permitrootlogin|passwordauth'
# expect: permitrootlogin yes / passwordauthentication yes
```

Notes
- If `PermitRootLogin prohibit-password` is correct by policy, install an SSH key instead
  (`ssh-copy-id root@<ct-ip>`) — do NOT enable password root login just to make SSH work.
- A key in `/etc/ssh/sshd_config.d/*.conf` can override the main file; check there too.
- First confirm the real symptom before changing anything: is sshd listening? (`ss -tlnp | grep :22`)
  Is the port reachable from the host? (`cat < /dev/null > /dev/tcp/<ct-ip>/22`) Is there a
  PVE firewall rule (`/etc/pve/firewall/101.fw`)? Only then blame sshd_config.