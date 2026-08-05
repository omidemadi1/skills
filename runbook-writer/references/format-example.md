# Format Example

This is a worked example of the target format, drawn from a real server-setup runbook. Use it as the template for heading depth, step numbering, code blocks, placeholders, and tone — not as literal content to copy.

---

## Config

### Network Setting

#### DNS Setting

1. `nano /etc/resolv.conf`
2. Add DNS address like this: `nameserver 1.1.1.1`

#### Routing: USB Tethering — NIC1: LAN, NIC2: Internet

1. Change the dynamic network card name to static
   1. Find the MAC address: `ip -br link`
   2. `nano /etc/systemd/network/10-usb-tether.link`
   3. Add these lines:

      ```text
      [Match]
      MACAddress=aa:bb:cc:dd:ee:ff

      [Link]
      Name=usbwan0
      ```

   4. `update-initramfs -u`
   5. `reboot`
2. `nano /etc/sysctl.conf`
3. Uncomment this line: `net.ipv4.ip_forward=1`
4. `sysctl -p`
5. NAT setting:

   ```bash
   iptables -t nat -F
   iptables -t nat -A POSTROUTING -o usbwan0 -j MASQUERADE
   iptables -A FORWARD -i vmbr0 -o usbwan0 -j ACCEPT
   iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
   ```

6. `nano /etc/network/interfaces`
7. Add these lines:

   ```text
   auto lo
   iface lo inet loopback

   allow-hotplug <Network-Card>
   iface <Network-Card> inet dhcp

   auto vmbr0
   iface vmbr0 inet static
       address <IP-Address/Subnet-Prefix>
       bridge-ports <Internet-Network-Card>
       bridge-stp off
       bridge-fd 0
   ```

8. `systemctl restart networking`
9. `dhclient usbwan0`

#### Remove Subscription Error

1. `cd /etc/apt/sources.list.d/`
2. Open the `pve-enterprise` file with `nano` and comment out all lines
3. Open the `ceph` file with `nano` and comment out all lines
4. Create the no-subscription source:

   ```bash
   cat >/etc/apt/sources.list.d/pve-no-subscription.sources <<EOF
   Types: deb
   URIs: http://download.proxmox.com/debian/pve
   Suites: trixie
   Components: pve-no-subscription
   Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
   EOF
   ```

## Disks

### Create LVM-Thin

Best used for SSD storage backing VMs.

1. Format the hard drive
   1. `lsblk`
   2. `sgdisk --zap-all /dev/<Hard-Disk>`
   3. `wipefs -a /dev/<Hard-Disk>`
2. If it still needs formatting, use Datacenter > Node > Disks > Wipe Disk
3. Go to Datacenter > Node > Disks > LVM-Thin > Create:

   ```text
   Disk: <Hard-Disk>
   Name: <Storage-Name>
   ```

### Create New Directory (NTFS)

1. `apt install ntfs-3g`
2. `lsblk -f`
3. `mkdir /mnt/hdd`
4. `mount -t ntfs-3g /dev/<Disk-Partition> /mnt/hdd`
5. `blkid /dev/<Disk-Partition>` and copy the `UUID`
6. Add this line to `/etc/fstab` so it mounts on reboot: `UUID=1234-ABCD /mnt/hdd ntfs-3g defaults,uid=0,gid=0 0 0`
7. Go to Datacenter > Storage > Add > Directory:

   ```text
   ID: <Directory-Name>
   Directory: /mnt/<Hard-Name>
   Content: Disk image, Container, ISO, Backup
   ```

### Mount Hard Disk to Node

1. Mount the hard disk on the host system (see "Create New Directory" above)
2. `pct set <Node-ID> -mp0 <Mounted-Directory>,mp=<Target-Directory>`

---

## When a section can't be verified live

Everything above was actually run and confirmed. When that's not possible — no access to the account/system in question, or documenting something the user already did elsewhere — flag it plainly instead of presenting a guess with the same confidence as a tested step:

### Stripe Account Setup

**Not verified live — based on Stripe's documented onboarding flow; menu labels may have changed since.**

1. Go to `https://dashboard.stripe.com/register` and sign up with `<Business-Email>`
2. Add a payout bank account: Settings (gear icon) > Business > **Bank accounts and currencies** tab > Add a bank account
3. Enter `<Bank-Routing-Number>` and `<Bank-Account-Number>`

## What to notice about this example

- Headings form a topic tree (`Config` → `Network Setting` → `DNS Setting`), not a timeline.
- Every step is something to literally type or click — no "then check if it worked" narration.
- A short one-line note ("Best used for SSD storage backing VMs") appears only where the purpose of a section isn't obvious from its heading.
- Placeholders (`<Hard-Disk>`, `<IP-Address/Subnet-Prefix>`) mark anything that depends on the reader's own setup.
- Nothing here hints that an earlier attempt failed, even though in practice something usually needs a second try — that trial and error is invisible in the final document.
- The one exception to "confident, tested-sounding steps" is when something genuinely wasn't verified — that gets a visible flag instead of being smoothed over.
