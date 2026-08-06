# Proxmox API Token Permission Debugging Guide

## Common Permission Issues

### 1. "Permission check failed" Errors
```
ERROR 403: None
Permission check failed (/vms/105, VM.Audit)
Permission check failed (/storage/local-lvm, Datastore.Audit|Datastore.AllocateSpace)
```

### Root Causes
1. **Missing explicit permissions on API token** (most common)
   - Token created with `separate=1` (privilege separation) but no permissions granted
   - Token needs explicit permissions even if user has Administrator role

2. **Incorrect permission path**
   - Permissions set on wrong path (e.g., `/` instead of `/vms/105`)
   - Need permissions on specific resource paths

3. **Wrong privilege type**
   - Trying to use `Sys.Audit` when need `VM.Audit`
   - Need specific privilege for operation type

## Debugging Commands

### Check What Resources Exist
```bash
# Check if VM exists as QEMU
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/qemu/VMID/config"

# Check if VM exists as LXC
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/lxc/VMID/config"
```

### Check Available Permissions
```bash
# List available roles
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/access/roles"

# Check token info (if endpoint available)
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/access/tokeninfo"
```

### Test Specific Permissions
```bash
# Test VM.Audit permission (read status)
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/qemu/VMID/status/current"

# Test VM.PowerMgmt permission (start)
curl -sk -X POST -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/qemu/VMID/status/start"

# Test Datastore.Audit permission (list storage)
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/storage/STORAGE/content"
```

## Fixing Permission Issues

### Method 1: Disable Privilege Separation (Simplest)
In Proxmox Web UI:
1. Datacenter → Permissions → API Tokens
2. Edit your token (e.g., `hermes@pve!full-access`)
3. **Uncheck** "Privilege Separation"
4. Token now inherits user's permissions

### Method 2: Grant Explicit Permissions (More Secure)
In Proxmox Web UI:
1. Datacenter → Permissions → API Tokens
2. Edit your token
3. Click **Add** under Permissions
4. Set:
   - Path: `/` (for full access) or specific path like `/vms/105`
   - User: `USER@REALM!TOKEN` (your token)
   - Role: `Administrator` or `PVEVMAdmin` (for VM management)
5. Click Add

### Method 3: Grant Minimum Required Permissions
For basic VM/CT management, grant these privileges on path `/`:
- `Sys.Audit` (view node status)
- `VM.Audit` (view VM/CT status/config)
- `VM.PowerMgmt` (start/stop/shutdown/reboot)
- `VM.Config.*` (as needed for config changes)
- `Datastore.Audit` (list storage/templates/ISOs)
- `Datastore.Allocate` (create resources)

## Quick Permission Check Reference

| Operation | Needed Privilege |
|-----------|------------------|
| `status vm/<vmid>` or `status ct/<vmid>` | `VM.Audit` |
| `start <vmid>`, `stop <vmid>`, `shutdown <vmid>`, `reboot <vmid>` | `VM.PowerMgmt` |
| `config vm <vmid> key=value` | `VM.Config.*` (specific area) |
| `create vm` or `create ct` | `VM.Allocate` + `Datastore.Allocate` |
| `delete <vmid>` | `VM.Allocate` (on the VM) |
| `list vms` or `list containers` | `VM.Audit` |
| `list templates` or `list isos` | `Datastore.Audit` |
| `exec lxc <vmid> <cmd>` or `exec qemu <vmid> <cmd>` | `VM.Audit` + `VM.Console` |

## Critical: Two "Permission" Errors That Are NOT Permissions

### 1. `keyctl=1` → 403 "only allowed for root@pam" (even for Administrator token)
**Root cause:** This is a HARDCODED check in `/usr/share/perl5/PVE/LXC.pm` (line ~1732):
```perl
"changing feature flags (except nesting) is only allowed for root@pam"
```
- It checks `authuser eq 'root@pam'` — meaning **password auth as root@pam**, NOT the role.
- **API tokens CANNOT bypass this** — even a `root@pam!token` with privsep=0 gets the same 403.
- Verified empirically: `root@pam` token → 403; `root@pam` password auth → 200.
**Fix:** Set `keyctl=1` via host shell (not API):
```bash
ssh root@<host> "pct set <vmid> -features nesting=1,keyctl=1"
# or edit /etc/pve/lxc/<vmid>.conf directly:  features: nesting=1,keyctl=1
```
Or just use `nesting=1` only (sufficient for Docker).

### 2. `POST /nodes/{node}/lxc/{vmid}/exec` → 501 Not Implemented
**Root cause:** The API exec endpoint **does not exist** in PVE 9.x. `pvesh ls /nodes/{node}/lxc/{vmid}` shows only `termproxy`, `vncproxy`, `status`, `config`, etc. — no `exec` subdir.
- This is NOT a permission issue and NO token/ACL change can enable it.
- PVE 9 removed the HTTP exec API for LXC; only `pct exec` (CLI) and web console remain.
**Fix:** Use the host shell:
```bash
ssh root@<host> "pct exec <vmid> -- <command>"
```
For QEMU VMs, the agent exec endpoint still exists (needs `qemu-guest-agent` running + `VM.GuestAgent.*` perms).

## Troubleshooting Flow

1. **Get 403 error?** → Check privilege type in error message
2. **Can't list resources?** → Need `VM.Audit` or `Datastore.Audit`
3. **Can't start/stop?** → Need `VM.PowerMgmt`
4. **Can't modify config?** → Need specific `VM.Config.*` privilege
5. **Still failing after adding permissions?** → Check privilege separation setting