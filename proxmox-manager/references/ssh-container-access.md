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