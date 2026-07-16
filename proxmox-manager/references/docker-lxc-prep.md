# Preparing an LXC for Docker (Penpot, etc.)

When a user wants a container "ready for Docker" but not the app itself:

## 1. Create with nesting enabled
```bash
python scripts/proxmox_api.py create ct \
  --vmid <id> --hostname <name> --memory <MB> --cores <n> \
  --disk <GB> --template alpine --password <pass>
```
Then enable nesting (required for Docker-in-LXC):
```bash
python scripts/proxmox_api.py config ct <vmid> features=nesting=1
```
**Note:** `keyctl=1` can ONLY be set by `root@pam`, not by an API token (even Administrator).
If you need it: `pct set <vmid> -features nesting=1,keyctl=1` on the host, or edit
`/etc/pve/lxc/<vmid>.conf` directly. `nesting=1` alone is sufficient for Docker.

## 2. Install Docker
If the API `exec` endpoint works:
```bash
python scripts/proxmox_api.py exec lxc <vmid> "apk add docker openrc && rc-update add docker default && service docker start"
```
(Debian/Ubuntu: `apt-get install -y docker.io docker-compose` + `systemctl enable --now docker`)

## 3. If API exec returns 501 (not implemented)
The node has exec disabled. Fall back to the **Proxmox host shell**:
```bash
ssh root@<proxmox-host> "pct exec <vmid> -- apk add docker openrc"
ssh root@<proxmox-host> "pct exec <vmid> -- sh -c 'rc-update add docker default && service docker start'"
```
`pct exec` on the host works even when the API exec endpoint is disabled.

## 4. Slow networks / apk lock contention
Alpine apk can be slow on high-latency links. If a previous `pct exec` timed out,
the apk process may still hold the lock:
```bash
# On the host:
pct exec <vmid> -- ps aux | grep apk          # find stale PID
pct exec <vmid> -- kill -9 <pid>              # kill it
pct exec <vmid> -- rm -f /var/lib/apk/db/lock # clear lock
```
Then retry the install in the background (long-running):
```bash
ssh root@<host> 'pct exec <vmid> -- sh -c "apk add docker openrc > /tmp/inst.log 2>&1; rc-update add docker default >> /tmp/inst.log 2>&1; service docker start >> /tmp/inst.log 2>&1; echo DONE >> /tmp/inst.log"' &
```

## 5. Verify
```bash
pct exec <vmid> -- docker --version
pct exec <vmid> -- docker ps
pct exec <vmid> -- rc-service docker status
```
