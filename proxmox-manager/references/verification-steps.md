# Proxmox Connection Verification Steps

## Quick Verification Commands

### 1. Check Version/Connectivity
```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/version"
```

### 2. List Nodes (Verify Node Name)
```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes"
```

### 3. Check Cluster Resources
```bash
# List all VMs
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/cluster/resources?type=vm"

# List all containers (if supported)
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/cluster/resources?type=lxc"
```

### 4. Check Storage Content
```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/storage/STORAGE/content"
```

### 5. Test Specific VMID as VM
```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/qemu/VMID/config"
```

### 6. Test Specific VMID as Container
```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/lxc/VMID/config"
```

## Expected Responses

### Success (200 OK)
```json
{
  "data": {
    // Resource data here
  }
}
```

### Permission Error (403)
```json
{
  "data": null,
  "message": "Permission check failed (/path/to/resource, PRIVILEGE.REQUIRED)"
}
```

### Not Found (404)
```json
{
  "data": null,
  "message": "Resource not found: /path/to/resource"
}
```

### Wrong Node Name (Hostname Resolution Error)
```json
{
  "data": null,
  "message": "hostname lookup 'wrong-node-name' failed - failed to get address info for: wrong-node-name: Name or service not known"
}
```

## Common Node Names to Check
If default `pve` doesn't work, try:
- The actual hostname of your Proxmox server
- Often found in: `pvecm status` or `hostnamectl` on the Proxmox host
- Common examples: `pve`, `proxmox`, `host1`, `server01`, or your actual server name

## Using the Proxmox API Script
When using `scripts/proxmox_api.py`, the script will:
1. Automatically load config from `scripts/proxmox-config.json`
2. Show clear error messages for connection issues
3. Poll tasks until completion for mutating operations
4. Return formatted output for list/status commands

Additional diagnostic tools:
- `scripts/proxmox-diagnose.py` - Run this to comprehensively test connectivity and permissions
  ```bash
  # Make executable (if needed)
  chmod +x scripts/proxmox-diagnose.py
  
  # Run diagnostic
  python scripts/proxmox-diagnose.py
  ```

Example debugging workflow with the script:
```bash
# Check if config is valid
cat scripts/proxmox-config.json

# Test basic connectivity
python scripts/proxmox_api.py status node

# List resources to test permissions
python scripts/proxmox_api.py list vms
python scripts/proxmox_api.py list containers

# Check specific resource
python scripts/proxmox_api.py status vm 105
python scripts/proxmox_api.py status ct 105
```

Example debugging workflow with the script:
```bash
# Check if config is valid
cat scripts/proxmox-config.json

# Test basic connectivity
python scripts/proxmox_api.py status node

# List resources to test permissions
python scripts/proxmox_api.py list vms
python scripts/proxmox_api.py list containers

# Check specific resource
python scripts/proxmox_api.py status vm 105
python scripts/proxmox_api.py status ct 105
```