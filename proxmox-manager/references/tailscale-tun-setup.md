# Enabling TUN for LXC containers (e.g., Tailscale)

When a container needs a virtual network interface (TUN) – for example when running **Tailscale** – the default LXC configuration on Proxmox does **not** expose `/dev/net/tun`. This results in the daemon exiting with errors such as:
```
CreateTUN("tailscale0") failed; /dev/net/tun does not exist
```

## Required host‑side steps (two approaches)

### Approach A: Edit the LXC config file directly (fallback when API rejects it)

The Proxmox API may reject `lxc.cgroup2.devices.allow` and `lxc.mount.entry` as "property is not defined in schema" — in that case, edit the config file directly on the Proxmox host:

```bash
# Edit /etc/pve/lxc/<VMID>.conf on the Proxmox host
# Add these lines to the MAIN config section (top block, not inside a snapshot block):
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

The mount entry **must** go in the main (active) config section, not just inside a `[snapshot-name]` block — LXC only reads the active section on boot.

1. **Edit the config** (replace `<VMID>` with the container ID):
   ```bash
   nano /etc/pve/lxc/<VMID>.conf
   ```
   Add two lines to the end of the top section (before any `[snapshot]` blocks):
   ```
   lxc.cgroup2.devices.allow: c 10:200 rwm
   lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
   ```

2. **Stop and start** the container (full stop/start, not just reboot):
   ```bash
   pct stop <VMID> && pct start <VMID>
   ```

**Key differences from Approach B:**
- Mounts the **device file directly** (`/dev/net/tun`) not the directory
- Uses `create=file` instead of `create=dir` (the directory already exists in the container's /dev via devtmpfs)
- Avoids the `optional` flag that lets mount failures pass silently

### Approach B: Use `pct set` (works on some Proxmox versions)

```bash
pct set <VMID> \
    -features nesting=1 \
    -features keyctl=1 \
    -lxc.cgroup2.devices.allow "c 10:200 rwm" \
    -lxc.mount.entry "/dev/net dev/net none bind,optional,create=dir"
```

* `nesting=1` enables privileged‑mode helpers.
* `keyctl=1` is required for some TUN operations.
* `c 10:200 rwm` grants read/write/mknod access to the character device `/dev/net/tun` (major 10, minor 200).
* The bind‑mount makes the host's `/dev/net` directory (which contains the `tun` node) visible inside the container.

2. **Stop and start** the container (full stop/start, not just reboot) so the new cgroup and mount entries take effect:
   ```bash
   pct stop <VMID> && pct start <VMID>
   ```
3. **Verify inside the container**:
   ```bash
   ls -l /dev/net/tun
   # Should show something like: crw-rw---- 1 root root 10, 200 ...
   ```
4. **Start the Tailscale service** again:
   ```bash
   rc-service tailscale start
   rc-service tailscale status   # should report "started"
   ```

## Optional: install iptables helpers (not required for Tailscale to run, but removes warnings)
```bash
apk add iptables iptables-openrc
```

## Common pitfalls
- Trying to `modprobe tun` inside the container fails because the container does not have a `/lib/modules` tree. The correct approach is to expose the device from the host as shown above.
- Forgetting `keyctl=1` can cause `CreateTUN` to fail on newer kernels.
- If the container was created with `unprivileged: 1`, the above steps will still work as long as the host grants the device permission via the `cgroup2.devices.allow` line.
- **Mount entry in wrong section**: The `lxc.mount.entry` MUST be in the main (active) config section, not inside a `[snapshot-name]` block. Snapshots restore the original config — put it before any snapshot blocks.
- **Stop/start not reboot**: Use `pct stop && pct start`, not `pct reboot`. A full restart ensures LXC re-reads the config and applies the bind mount.
- If both approaches above fail, try the **manual mknod fallback** (see below).

## Manual mknod Fallback (when bind mount doesn't work)

If the `lxc.mount.entry` bind mount still doesn't produce `/dev/net/tun` inside the container, create the device node by mounting the container's rootfs from the Proxmox host:

```bash
# On the Proxmox host:
# 1. Find the container's block device
ls -la /dev/pve/vm-<VMID>-disk-*

# 2. Mount the filesystem
mkdir -p /mnt/ct<VMID>
mount /dev/pve/vm-<VMID>-disk-0 /mnt/ct<VMID>

# 3. Create the device node
mkdir -p /mnt/ct<VMID>/dev/net
mknod /mnt/ct<VMID>/dev/net/tun c 10 200
chmod 666 /mnt/ct<VMID>/dev/net/tun

# 4. Verify
ls -la /mnt/ct<VMID>/dev/net/tun
# Should show: crw-rw-rw- 1 root root 10, 200

# 5. Unmount
umount /mnt/ct<VMID>
rmdir /mnt/ct<VMID>
```

After this, stop and start the container. The device node persists inside the container's filesystem even after restart.

## Tailscale Client + Subnet Routing

After TUN is enabled, install the Tailscale client and connect it to your headscale server:

```bash
# Install tailscale
apk add tailscale

# Enable IP forwarding
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding = 1" >> /etc/sysctl.conf
sysctl -p

# Enable and start tailscale
rc-update add tailscale default
rc-service tailscale start

# Connect to headscale (advertise subnet routes)
tailscale up \
  --login-server=http://<headscale-ip>:8080 \
  --auth-key=<preauth-key> \
  --advertise-routes=<LAN-CIDR> \
  --accept-routes
```

**After connecting, approve the routes in headscale:**
```bash
# On the headscale server:
headscale nodes list-routes                         # see available routes
headscale nodes approve-routes --identifier <node-id> --routes <CIDR>
```

Key flags:
- `--advertise-routes=192.168.1.0/24` makes this container act as a subnet router
- `--accept-routes` allows this node to use other nodes' advertised routes
- Route approval is required in headscale for the routes to be active

Save this reference for any future work requiring a TUN device inside LXC containers (WireGuard, Tailscale, OpenVPN, etc.).