# Installing Headscale on Alpine Linux LXC Container

Headscale is a self-hosted Tailscale control plane. Unlike Tailscale clients, **headscale does NOT need TUN device access** — it runs as a regular HTTP/gRPC server. This makes it simpler to deploy in LXC containers.

## Alpine Linux Package Availability

Headscale is in Alpine's community repository (v3.23+):

```bash
apk search headscale
# headscale-0.27.0-r6
# headscale-openrc-0.27.0-r6      # OpenRC service
# headscale-bash-completion-...
# headscale-fish-completion-...
# headscale-zsh-completion-...
```

Install both packages:
```bash
apk add headscale headscale-openrc
```

## OpenRC Service Management

```bash
# Enable on boot
rc-update add headscale default

# Start/stop/restart
rc-service headscale start
rc-service headscale stop
rc-service headscale restart
rc-service headscale status
```

## Configuration for LAN Access

Default config (`/etc/headscale/config.yaml`) listens on `127.0.0.1:8080`. Change to LAN:

```yaml
server_url: http://<CONTAINER_IP>:8080
listen_addr: 0.0.0.0:8080
grpc_listen_addr: 0.0.0.0:50443
grpc_allow_insecure: true
```

Then restart: `rc-service headscale restart`

## Creating Users & Pre-auth Keys

```bash
# Create admin user
headscale users create admin

# Create reusable pre-auth key (1 year, no expiry)
headscale preauthkeys create --user 1 --reusable --ephemeral=false --expiration 8760h
# Output: <key>  (e.g., 554aece6c3d649f58efdbca8445e60c000bf188d8fc6d24a)
```

## Onboarding Tailscale Clients

On each client device:
```bash
tailscale up --login-server=http://<CONTAINER_IP>:8080 --auth-key=<preauth-key>
```

## Useful Headscale Commands

```bash
headscale users list
headscale nodes list
headscale nodes list -o json              # detailed JSON (includes routes)
headscale nodes list-routes                # see advertised vs approved routes
headscale nodes approve-routes --identifier <node-id> --routes <CIDR>
headscale preauthkeys create --user <user-id> --reusable --expiration 8760h
headscale preauthkeys list --user <user-id>
headscale version
```

## Files & Paths

| Path | Purpose |
|------|---------|
| `/etc/headscale/config.yaml` | Main configuration |
| `/var/lib/headscale/db.sqlite` | SQLite database |
| `/var/lib/headscale/noise_private.key` | Noise protocol key |
| `/var/run/headscale/headscale.sock` | Unix socket for CLI |
| `/var/log/headscale.log` | Service logs |

## Notes

- Uses SQLite by default (recommended by headscale team)
- Public DERP servers from Tailscale work out of the box
- MagicDNS enabled by default with `example.com` base domain — change in config
- gRPC insecure mode enabled for CLI access from LAN
- Health check endpoint: `http://<IP>:8080/health`

## Proxmox-Specific

Container 103 (Remote-Access) config that worked:
- Alpine 3.23, 1 vCPU, 512MB RAM, 10G disk
- `features: nesting=1,keyctl=1` (already set)
- Static IP: `192.168.1.110/24` on `vmbr0`
- SSH access via Proxmox host network (exec endpoint returns 501)

## Running headscale + Tailscale Client on the Same Container

Headscale itself does NOT need TUN — it's a plain HTTP/gRPC server. But if you want the same container to also **act as a subnet router** for your Proxmox LAN, install the Tailscale client alongside:

### 1. Enable TUN on the container

See `references/tailscale-tun-setup.md` — both the cgroup device allow rule and bind mount are required.

### 2. Install and connect Tailscale

```bash
apk add tailscale
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding = 1" >> /etc/sysctl.conf
sysctl -p
rc-update add tailscale default
rc-service tailscale start

# Connect to the headscale server running on the same machine
tailscale up \
  --login-server=http://127.0.0.1:8080 \
  --auth-key=<preauth-key> \
  --advertise-routes=192.168.1.0/24 \
  --accept-routes
```

### 3. Approve subnet routes in headscale

```bash
headscale nodes list-routes
headscale nodes approve-routes --identifier <node-id> --routes 192.168.1.0/24
```

### 4. Client devices just need `--accept-routes` to reach the LAN

```bash
tailscale up --login-server=http://<headscale-ip>:8080 --auth-key=<key> --accept-routes
```

### Architecture

```
Phone (mobile data)
      │
      │ Tailscale (100.64.0.x)
      ▼
Container 103 (headscale + tailscale client)
      │ ─── server_url=http://...:8080  (headscale)
      │ ─── advertises 192.168.1.0/24  (subnet router)
      │
      ├── Proxmox host (192.168.1.10)
      ├── Container A (192.168.1.100)
      ├── Container B (192.168.1.101)
      └── Any LAN device
```