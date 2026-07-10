---
name: proxmox-manager
description: Manage Proxmox VE servers — VMs, LXCs, storage, networking, and guest command execution via the Proxmox REST API. Use when the user mentions proxmox, PVE, virtual machines, LXC containers, qemu, VM creation, server management, infrastructure provisioning, or wants to create, modify, troubleshoot, or delete Proxmox virtual environments. Always use this skill when Proxmox administration tasks are requested, even indirectly (e.g., "I need a server for my app").
---

# Proxmox Manager

Full lifecycle management of Proxmox VE via the REST API with API Token authentication. Manages nodes, VMs (QEMU), and containers (LXC).

## Workflow (Mandatory Order)

Every interaction with this skill follows three phases. **Never skip Phase 1 or 2.**

### Phase 1: Validate Connection

Before doing anything else, verify the config and test connectivity:

```bash
python scripts/proxmox_validate.py
```

**If validation fails:**
1. Show the error message to the user
2. Ask for corrected values (host, token_id, token_secret, node)
3. Write corrected values to `scripts/proxmox-config.json`
4. Re-run validation
5. Repeat until validation passes

**If `scripts/proxmox-config.json` doesn't exist:**
Collect these values from the user first:

| Field | Example | Description |
|-------|---------|-------------|
| `host` | `https://192.168.1.100:8006` | Proxmox server URL |
| `token_id` | `root@pam!my-token` | API token ID |
| `token_secret` | `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee` | API token secret |
| `node` | `pve` | Node name (use `list nodes` to verify) |
| `storage` | `local-lvm` | Default storage pool |
| `bridge` | `vmbr0` | Default network bridge |
| `verify_ssl` | `false` | SSL verification |

Write to `scripts/proxmox-config.json`:
```json
{
  "host": "https://192.168.1.100:8006",
  "token_id": "root@pam!my-token",
  "token_secret": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "node": "pve",
  "storage": "local-lvm",
  "bridge": "vmbr0",
  "verify_ssl": false
}
```

Then validate before proceeding.

### Phase 2: Discover Server Info

After successful validation, check for cached server info:

```bash
python scripts/proxmox_api.py discover   # writes scripts/proxmox-discovery.json
python scripts/proxmox_api.py cache      # view summary
python scripts/proxmox_api.py cache vms|containers|storages
```

**Auto-refresh rules:**
- If `scripts/proxmox-discovery.json` doesn't exist → run discover
- If `discovered_at` is older than 6 hours → run discover
- Otherwise → use cached data

**What gets cached:**
- All containers and VMs with status, IP, cores, memory, disk
- All storages with type and content
- Network interfaces
- Resource pools
- API tokens
- SDN zones and vnets

See `templates/server-info.json` for the full data structure.

### Phase 3: Execute Command

After validation and discovery, execute the user's command using cached info.

**API-first execution:**
Always use the API token for commands. Only fall back to SSH when API exec fails.

```bash
# API exec (preferred)
python scripts/proxmox_api.py exec lxc <vmid> "command"
python scripts/proxmox_api.py exec qemu <vmid> "command"

# Power operations
python scripts/proxmox_api.py start <vmid>
python scripts/proxmox_api.py stop <vmid>
python scripts/proxmox_api.py shutdown <vmid>

# Status
python scripts/proxmox_api.py status vm <vmid>
python scripts/proxmox_api.py status ct <vmid>
```

## SSH Fallback

When API exec returns **501 Not Implemented** or **403 Permission Denied**, fall back to SSH:

```bash
python scripts/proxmox_api.py ssh <vmid> "command"
```

**Collecting SSH credentials:**
When SSH fallback is needed but no credentials exist:

1. Inform user: "API exec failed. I need SSH credentials for this container."
2. Ask for: IP address, username, password
3. Ask permission: "Save these credentials for future use?"
4. If approved → write to `scripts/ssh-credentials.json`

SSH credentials file structure:
```json
{
  "encrypted": false,
  "credentials": [
    {
      "vmid": 105,
      "name": "container-name",
      "type": "lxc",
      "ip": "192.168.1.105",
      "user": "root",
      "password": "the-password"
    }
  ]
}
```

See `references/ssh-fallback.md` for full SSH documentation.

## API Script Reference

All operations use `scripts/proxmox_api.py`:

| Action | Purpose |
|--------|---------|
| `validate` | Test config and API connectivity |
| `discover` / `cache [category]` | Cache management |
| `list vms` / `list containers` | List all VMs / containers |
| `list templates` / `list isos` | Available CT templates / ISO images |
| `status node` | Node CPU, RAM, disk |
| `status vm <vmid>` / `status ct <vmid>` | VM or container details |
| `create vm <options>` | Create a new VM |
| `create ct <options>` | Create a new container |
| `config vm <vmid> <pairs>` | Modify VM config (key=value …) |
| `config ct <vmid> <pairs>` | Modify container config |
| `resize vm <vmid> <disk> <size>` | Enlarge VM disk (e.g. `+10G`) |
| `resize ct <vmid> <mp> <size>` | Enlarge container mount point |
| `start` / `stop` / `shutdown` / `reboot <vmid>` | Power operations |
| `delete <vmid>` | Delete VM or container |
| `exec lxc <vmid> <cmd>` | Run command in LXC container |
| `exec qemu <vmid> <cmd>` | Run command in VM (requires Guest Agent) |
| `ssh <vmid> <cmd>` | Run command via SSH (fallback) |
| `log <vmid>` / `tasks` | Recent task log |

**Key examples:**
```bash
python scripts/proxmox_api.py create ct \
  --vmid 200 --hostname web --memory 2048 --cores 2 \
  --disk 8 --template "ubuntu-22.04" --password "temp123!"

python scripts/proxmox_api.py config vm 100 memory=4096 cores=4
python scripts/proxmox_api.py resize vm 100 scsi0 +10G
python scripts/proxmox_api.py exec lxc 200 "apt-get update && apt-get install -y nginx"
```

If `requests` is not installed: `pip install requests`

## Resource Assessment

When the user doesn't specify exact specs, propose a configuration and **ask for approval** before creating.

### Spec guidelines

| Use Case | vCPUs | RAM | Disk | Type |
|----------|-------|-----|------|------|
| Static web server | 1 | 512MB–1GB | 4–8GB | LXC |
| Dynamic web app | 1–2 | 1–2GB | 8–16GB | LXC or VM |
| Database | 2–4 | 4–8GB | 32–64GB | VM |
| Media server | 2–4 | 2–4GB | 100GB+ | VM |
| Dev environment / CI runner | 2 | 2–4GB | 16–32GB | LXC |
| General purpose | 2 | 2GB | 16GB | LXC |

**VM vs LXC:** Prefer LXC for single-purpose, web, dev, or CI workloads. Use VM for custom kernels, Docker-in-Docker, Windows, or strong isolation. If unsure, propose LXC.

**Templates/ISOs:** Run `list templates` or `list isos` to see what's available. Prefer Ubuntu 22.04/24.04 or Debian 12 for LXC. Enable `agent=1` on VMs for Guest Agent support.

## Core Operations

**Pitfalls & Workarounds**
- The `exec` API endpoint may return **HTTP 501 Not Implemented**. Fall back to SSH.
- When using an API token, the token must have `VM.Console` permission to run `pct exec` commands. Otherwise **403 Permission check failed**.
- Refer to `references/exec-not-implemented.md` and `references/permission-debugging.md` for details.

### Listing & Status
```bash
python scripts/proxmox_api.py list vms
python scripts/proxmox_api.py list containers
python scripts/proxmox_api.py status node
python scripts/proxmox_api.py status ct 200
```

### Creating Resources
```bash
# Container
python scripts/proxmox_api.py create ct \
  --vmid <auto|number> --hostname <name> --memory <MB> \
  --cores <count> --disk <GB> --template <name> --password <pass>

# VM
python scripts/proxmox_api.py create vm \
  --vmid <auto|number> --name <name> --memory <MB> \
  --cores <count> --disk <GB> --ostype <l26|win10|...>
```
`--vmid` auto-selects next available if omitted.

### Config & Resize
```bash
python scripts/proxmox_api.py config vm 100 memory=4096 cores=4
python scripts/proxmox_api.py config ct 200 memory=2048 swap=1024
python scripts/proxmox_api.py resize vm 100 scsi0 +10G   # enlarge only
```

**Known limitation — custom LXC properties:** The Proxmox API does NOT support setting arbitrary LXC properties such as `lxc.cgroup2.devices.allow`, `lxc.mount.entry`, `lxc.hook.*`, etc. These must be set by editing `/etc/pve/lxc/<VMID>.conf` **directly on the Proxmox host**. See `references/tailscale-tun-setup.md` for the TUN device example.

### Power & Delete
```bash
python scripts/proxmox_api.py start 100
python scripts/proxmox_api.py shutdown 100   # graceful
python scripts/proxmox_api.py stop 100       # force
python scripts/proxmox_api.py delete 100
```

### Guest Command Execution
```bash
# LXC (API preferred)
python scripts/proxmox_api.py exec lxc 200 "systemctl start nginx"

# VM (requires QEMU Guest Agent)
python scripts/proxmox_api.py exec qemu 100 "apt-get install -y postgresql"

# SSH fallback (when API exec fails)
python scripts/proxmox_api.py ssh 200 "systemctl start nginx"
```

Run commands sequentially for multi-step setups — check output at each step.

**501 Not Implemented:** Some installations disable the exec endpoint. See `references/exec-not-implemented.md`.

**Tailscale in LXC:** Requires TUN device access. See `references/tailscale-tun-setup.md`.

## Troubleshooting

When a problem is reported:
1. `status vm/ct <vmid>` — check current state
2. `status node` — check resource pressure
3. `tasks <vmid>` — recent task errors
4. Check config matches expectations

**For connectivity/permission issues on first setup**, read `references/permission-debugging.md`. Key traps:
- Wrong node name (`pve` may not be your actual node — use `list nodes` to check)
- API token with Privilege Separation enabled but no explicit permissions granted → fix in UI or set `separate=0`

**For SSH access to containers**, see `references/ssh-container-access.md` and `references/ssh-fallback.md`.

**For detailed verification curl commands**, see `references/verification-steps.md`.

**Present your diagnosis and proposed fix before taking action.**

## Safety Rules

- **ASK BEFORE** any destructive action: delete, stop, shutdown, reboot, resize, or significant config changes
- **ASK BEFORE** creating — present full proposed spec for approval
- **ASK BEFORE** saving SSH credentials — confirm user wants to store them
- **NEVER** modify or delete without explicit confirmation
- **NEVER** print or log SSH passwords
- Show errors to the user and suggest a fix
- Disk resize: enlargement only — shrinking is not supported

## Inter-skill Interface

When called by another skill, accept:
```
request: <description of what machine to create and what to install>
```

Workflow: validate → discover → assess specs → present plan → create on approval → install software → report back. Do **not** return IPs, VMIDs, or internal details as actionable outputs — all further management must come back through this skill.
