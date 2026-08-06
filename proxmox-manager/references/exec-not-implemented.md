# LXC/VM Exec Endpoint Not Implemented

## Symptom

When attempting to execute commands inside a container or VM using the Proxmox API, you receive:

```
HTTP 501: Method 'POST /nodes/{node}/lxc/{vmid}/exec' not implemented
```

or

```
HTTP 501: Method 'POST /nodes/{node}/qemu/{vmid}/agent/exec' not implemented
```

## Cause

This occurs on certain Proxmox VE versions (observed on 8.4.19) where the exec endpoint is disabled or not present in the pve-manager API. This can be due to:

- Security hardening that disables the exec feature
- Specific kernel/modules configuration
- The feature being turned off in the Proxmox configuration
- Version-specific API differences

## Verification

You can test the endpoint directly:

```bash
curl -sk -H "Authorization: PVEAPIToken=USER@REALM!TOKEN" \
  -X POST "https://PROXMOX_HOST:8006/api2/json/nodes/NODE/lxc/VMID/exec" \
  -d '{"command":"echo hello"}'
```

If you receive a 501 response with "not implemented", the endpoint is unavailable.

## Workarounds

### 1. Use `pct exec` on the Proxmox Host (preferred for LXC)
The container exec endpoint is disabled, but `pct exec` still works on the host:
```bash
ssh root@<proxmox-host> "pct exec <vmid> -- <command>"
```
This is the most reliable workaround — it requires only host SSH access (root).

### 2. Use the Proxmox Web Console
- Navigate to Node → LXC/CTID → Console in the web UI
- Provides direct shell access
- No API token permissions needed beyond console access

### 3. Startup/Hook Scripts
Configure the container to run commands on boot:

```bash
# Set via API (if config endpoint works)
python scripts/proxmox_api.py config ct 103 \
  hooks='{ "startup": "/usr/local/bin/install-tailscale.sh" }'
```

Then place your script at the specified path inside the container's filesystem.

### 3. Filesystem Modification
For LXC containers, you can mount the container's disk and edit files:

1. Stop the container
2. Mount the rootfs: `mount /dev/pve/vm-103-disk-0 /mnt`
3. Edit files under `/mnt`
4. Unmount and start

### 4. Use Host as Jump Point
Since the container uses the Proxmox host as its gateway:
- Install software on the host
- Use bind mounts or network filesystems to make it available
- Configure the container to use host-installed software

### 5. Build Custom Container Image
Create a new template with pre-installed software:
- Download a base template
- Customize it with your needed packages
- Use it for future container creation

## Prevention

When setting up new Proxmox instances, verify the exec endpoint works:

```bash
# Test on a known container/VM
curl -sk -H "Authorization: PVEAPIToken=..." \
  -X POST "https://host:8006/api2/json/nodes/node/lxc/100/exec" \
  -d '{"command":"echo test"}'
```

If it fails, note the limitation for automation scripts.