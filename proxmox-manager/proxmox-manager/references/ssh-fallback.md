# SSH Fallback for Proxmox Command Execution

## Overview

When the Proxmox API exec endpoint is unavailable (HTTP 501) or permission is denied (HTTP 403), the skill falls back to SSH for running commands inside containers and VMs.

## Priority Order

1. **API Token exec** — Always tried first (fastest, no extra credentials needed)
2. **SSH** — Used only when API exec fails and SSH credentials are available

## SSH Credentials File

Located at `scripts/ssh-credentials.json`:

```json
{
  "encrypted": false,
  "credentials": [
    {
      "vmid": 105,
      "name": "my-container",
      "type": "lxc",
      "ip": "192.168.1.105",
      "user": "root",
      "password": "the-password"
    }
  ]
}
```

## Collecting Credentials

When SSH fallback is needed but no credentials exist for the target:

1. Inform the user: "API exec is unavailable for container 105. I need SSH credentials to proceed."
2. Ask for: IP address, username, password
3. Ask permission: "Save these credentials for future use?"
4. If approved → write to `scripts/ssh-credentials.json`
5. Execute the command via SSH

## Encrypted Mode

When `encrypted: true`, passwords are GPG-encrypted:

```bash
# Encrypt
echo -n "password" | gpg --symmetric --batch --passphrase-fd 0 -o /dev/stdout | base64

# Decrypt
echo "base64ciphertext" | base64 -d | gpg --decrypt --batch --passphrase-fd 0
```

## SSH Execution Methods

### Direct SSH (preferred)
```bash
sshpass -p '<password>' ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@<ip> "<command>"
```

### Via Proxmox Host (if container has no direct network access)
```bash
ssh root@<proxmox-host> "pct exec <vmid> -- <command>"
```

## Prerequisites

- `sshpass` must be installed: `apt-get install -y sshpass`
- Container/VM must have SSH server running
- Network route from agent to container IP must exist

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `sshpass: command not found` | sshpass not installed | Run `apt-get install -y sshpass` |
| `Connection refused` | SSH server not running | Start sshd inside container |
| `No route to host` | Network not configured | Check bridge/network config |
| `Permission denied` | Wrong password | Verify credentials |
| `Host key verification failed` | First connection | Use `-o StrictHostKeyChecking=no` |
