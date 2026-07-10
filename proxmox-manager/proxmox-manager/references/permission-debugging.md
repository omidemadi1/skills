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

## Troubleshooting Flow

1. **Get 403 error?** → Check privilege type in error message
2. **Can't list resources?** → Need `VM.Audit` or `Datastore.Audit`
3. **Can't start/stop?** → Need `VM.PowerMgmt`
4. **Can't modify config?** → Need specific `VM.Config.*` privilege
5. **Still failing after adding permissions?** → Check privilege separation setting