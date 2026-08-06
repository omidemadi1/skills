#!/usr/bin/env python3
"""
Proxmox VE API CLI helper.

Usage:
    python proxmox_api.py list vms
    python proxmox_api.py list containers
    python proxmox_api.py list templates
    python proxmox_api.py list isos
    python proxmox_api.py status node
    python proxmox_api.py status vm <vmid>
    python proxmox_api.py status ct <vmid>
    python proxmox_api.py create vm [options]
    python proxmox_api.py create ct [options]
    python proxmox_api.py config vm <vmid> key=value [key=value ...]
    python proxmox_api.py config ct <vmid> key=value [key=value ...]
    python proxmox_api.py resize vm <vmid> <disk> <size>
    python proxmox_api.py resize ct <vmid> <mountpoint> <size>
    python proxmox_api.py start <vmid>
    python proxmox_api.py stop <vmid>
    python proxmox_api.py shutdown <vmid>
    python proxmox_api.py reboot <vmid>
    python proxmox_api.py delete <vmid>
    python proxmox_api.py exec lxc <vmid> <command>
    python proxmox_api.py exec qemu <vmid> <command>
    python proxmox_api.py log <vmid>
    python proxmox_api.py tasks
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "proxmox-config.json")
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    
    config.setdefault("host", os.environ.get("PROXMOX_HOST", ""))
    config.setdefault("token_id", os.environ.get("PROXMOX_API_TOKEN_ID", ""))
    config.setdefault("token_secret", os.environ.get("PROXMOX_API_TOKEN_SECRET", ""))
    config.setdefault("node", os.environ.get("PROXMOX_NODE", ""))
    config.setdefault("storage", os.environ.get("PROXMOX_STORAGE", "local-lvm"))
    config.setdefault("bridge", os.environ.get("PROXMOX_BRIDGE", "vmbr0"))
    verify = os.environ.get("PROXMOX_VERIFY_SSL", "0")
    config.setdefault("verify_ssl", verify == "1")
    
    missing = [k for k in ("host", "token_id", "token_secret", "node") if not config.get(k)]
    if missing:
        print(f"ERROR: Missing required config: {', '.join(missing)}")
        print("Set them in scripts/proxmox-config.json or as environment variables.")
        sys.exit(1)
    
    return config


def api_request(config, method, path, params=None, data=None):
    url = f"{config['host'].rstrip('/')}/api2/json{path}"
    headers = {
        "Authorization": f"PVEAPIToken={config['token_id']}={config['token_secret']}"
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    
    try:
        resp = requests.request(
            method, url,
            headers=headers,
            params=params,
            json=data,
            verify=config["verify_ssl"],
            timeout=60
        )
    except requests.exceptions.SSLError:
        print("WARNING: SSL verification failed. Set verify_ssl to false or fix your certificates.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Cannot connect to {config['host']}: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
        sys.exit(1)
    
    if resp.status_code >= 400:
        try:
            err = resp.json()
            msg = err.get("errors", err.get("data", str(err)))
        except Exception:
            msg = resp.text
        print(f"ERROR {resp.status_code}: {msg}")
        sys.exit(1)
    
    return resp.json().get("data")


def poll_task(config, node, upid, label="Task"):
    """Poll an async task until it completes."""
    encoded = urllib.parse.quote(upid, safe="")
    print(f"  {label} started. Waiting...", end="", flush=True)
    while True:
        status = api_request(config, "GET", f"/nodes/{node}/tasks/{encoded}/status")
        if status is None:
            print(" done.")
            return
        if status.get("exitstatus") == "OK":
            print(" done.")
            return
        if status.get("status") == "stopped" and status.get("exitstatus") != "OK":
            print(f" failed: {status.get('exitstatus', 'unknown error')}")
            sys.exit(1)
        time.sleep(1)
        print(".", end="", flush=True)


def get_next_vmid(config):
    """Get the next available VMID."""
    resources = api_request(config, "GET", "/cluster/resources", params={"type": "vm"})
    vmids = [r["vmid"] for r in resources] if resources else []
    return max(vmids) + 1 if vmids else 100


def get_storage_content(config, content_type):
    storage = config["storage"]
    return api_request(config, "GET", f"/nodes/{config['node']}/storage/{storage}/content",
                       params={"content": content_type})


def discover_and_cache(config):
    """Discover and cache useful Proxmox server information."""
    node = config["node"]
    cache = {
        "discovered_at": time.time(),
        "node": node,
        "storages": [],
        "vms": [],
        "containers": [],
        "users": [],
        "api_tokens": [],
        "pools": [],
        "networks": [],
        "sdn_zones": [],
        "sdn_vnets": [],
    }

    print("Discovering Proxmox server information...")

    # 1. Discover storages
    print("  - Fetching storages...")
    storages = api_request(config, "GET", f"/nodes/{node}/storage")
    if storages:
        cache["storages"] = storages
        print(f"    Found {len(storages)} storage(s)")

    # 2. Discover VMs
    print("  - Fetching VMs...")
    vms = api_request(config, "GET", f"/nodes/{node}/qemu")
    if vms:
        # Get detailed config for each VM
        detailed_vms = []
        for vm in vms:
            vmid = vm.get("vmid")
            if vmid:
                config_data = api_request(config, "GET", f"/nodes/{node}/qemu/{vmid}/config")
                if config_data:
                    vm["detailed_config"] = config_data
                status_data = api_request(config, "GET", f"/nodes/{node}/qemu/{vmid}/status/current")
                if status_data:
                    vm["detailed_status"] = status_data
            detailed_vms.append(vm)
        cache["vms"] = detailed_vms
        print(f"    Found {len(vms)} VM(s)")

    # 3. Discover containers (LXCs)
    print("  - Fetching containers...")
    containers = api_request(config, "GET", f"/nodes/{node}/lxc")
    if containers:
        detailed_containers = []
        for ct in containers:
            vmid = ct.get("vmid")
            if vmid:
                config_data = api_request(config, "GET", f"/nodes/{node}/lxc/{vmid}/config")
                if config_data:
                    ct["detailed_config"] = config_data
                status_data = api_request(config, "GET", f"/nodes/{node}/lxc/{vmid}/status/current")
                if status_data:
                    ct["detailed_status"] = status_data
            detailed_containers.append(ct)
        cache["containers"] = detailed_containers
        print(f"    Found {len(containers)} container(s)")

    # 4. Discover users
    print("  - Fetching users...")
    users = api_request(config, "GET", "/access/users")
    if users:
        cache["users"] = users
        print(f"    Found {len(users)} user(s)")

    # 5. Discover API tokens
    print("  - Fetching API tokens...")
    all_tokens = []
    users_data = api_request(config, "GET", "/access/users")
    if users_data:
        for user in users_data:
            userid = user.get("userid")
            if userid:
                user_tokens = api_request(config, "GET", f"/access/users/{urllib.parse.quote(userid, safe='')}/token")
                if user_tokens:
                    for token in user_tokens:
                        token["userid"] = userid
                        all_tokens.append(token)
    cache["api_tokens"] = all_tokens
    print(f"    Found {len(all_tokens)} API token(s)")

    # 6. Discover pools
    print("  - Fetching resource pools...")
    pools = api_request(config, "GET", "/pools")
    if pools:
        cache["pools"] = pools
        print(f"    Found {len(pools)} pool(s)")

    # 7. Discover networks (bridge interfaces on node)
    print("  - Fetching network configuration...")
    networks = api_request(config, "GET", f"/nodes/{node}/network")
    if networks:
        cache["networks"] = networks
        print(f"    Found {len(networks)} network interface(s)")

    # 8. Discover SDN zones (if SDN is configured)
    print("  - Fetching SDN zones...")
    sdn_zones = api_request(config, "GET", "/cluster/sdn/zones")
    if sdn_zones:
        cache["sdn_zones"] = sdn_zones
        print(f"    Found {len(sdn_zones)} SDN zone(s)")

    # 9. Discover SDN VNets
    print("  - Fetching SDN VNets...")
    sdn_vnets = api_request(config, "GET", "/cluster/sdn/vnets")
    if sdn_vnets:
        cache["sdn_vnets"] = sdn_vnets
        print(f"    Found {len(sdn_vnets)} SDN VNet(s)")

    # Save to cache file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, "proxmox-discovery.json")
    
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2, default=str)
    
    print(f"\n✓ Discovery complete! Cached to {cache_path}")
    print(f"  Storages: {len(cache['storages'])}")
    print(f"  VMs: {len(cache['vms'])}")
    print(f"  Containers: {len(cache['containers'])}")
    print(f"  Users: {len(cache['users'])}")
    print(f"  API Tokens: {len(cache['api_tokens'])}")
    print(f"  Pools: {len(cache['pools'])}")
    print(f"  Networks: {len(cache['networks'])}")
    print(f"  SDN Zones: {len(cache['sdn_zones'])}")
    print(f"  SDN VNets: {len(cache['sdn_vnets'])}")
    
    return cache


# ---------------------------------------------------------------------------
# Action implementations
# ---------------------------------------------------------------------------

def cmd_list(args, config):
    node = config["node"]
    if args.list_type == "vms":
        data = api_request(config, "GET", f"/nodes/{node}/qemu")
        if not data:
            print("No VMs found.")
            return
        print(f"{'VMID':<8} {'NAME':<20} {'STATUS':<10} {'MEM':<8} {'CPU':<6}")
        print("-" * 60)
        for vm in sorted(data, key=lambda x: x.get("vmid", 0)):
            print(f"{vm.get('vmid', '?'):<8} {vm.get('name', '?'):<20} "
                  f"{vm.get('status', '?'):<10} {vm.get('mem', 0)//1024//1024 if vm.get('mem') else 0:<8} "
                  f"{vm.get('cpus', '?'):<6}")
    elif args.list_type == "containers":
        data = api_request(config, "GET", f"/nodes/{node}/lxc")
        if not data:
            print("No containers found.")
            return
        print(f"{'VMID':<8} {'HOSTNAME':<20} {'STATUS':<10} {'MEM':<8} {'CPU':<6}")
        print("-" * 60)
        for ct in sorted(data, key=lambda x: x.get("vmid", 0)):
            print(f"{ct.get('vmid', '?'):<8} {ct.get('name', '?'):<20} "
                  f"{ct.get('status', '?'):<10} {ct.get('mem', 0)//1024//1024 if ct.get('mem') else 0:<8} "
                  f"{ct.get('cpus', '?'):<6}")
    elif args.list_type == "templates":
        storage = args.storage or config["storage"]
        items = api_request(config, "GET", f"/nodes/{config['node']}/storage/{storage}/content", params={"content": "vztmpl"})
        if not items or not isinstance(items, list):
            print(f"No container templates found on storage '{storage}'.")
            return
        print(f"Available container templates on {storage}:")
        for item in sorted(items, key=lambda x: x.get("volid", "")):
            v = item.get("volid", "?")
            size = item.get("size", 0)
            size_mb = size // (1024 * 1024) if size else 0
            print(f"  {v} ({size_mb} MB)")
    elif args.list_type == "isos":
        storage = args.storage or config["storage"]
        items = api_request(config, "GET", f"/nodes/{config['node']}/storage/{storage}/content", params={"content": "iso"})
        if not items or not isinstance(items, list):
            print(f"No ISO images found on storage '{storage}'.")
            return
        print(f"Available ISO images on {storage}:")
        for item in sorted(items, key=lambda x: x.get("volid", "")):
            print(f"  {item.get('volid', '?')}")


def cmd_status(args, config):
    node = config["node"]
    if args.status_type == "node":
        data = api_request(config, "GET", f"/nodes/{node}/status")
        if not data:
            return
        print(f"Node:        {node}")
        print(f"Version:     {data.get('pveversion', '?')}")
        print(f"Kernel:      {data.get('kversion', '?')}")
        print(f"Uptime:      {data.get('uptime', 0) // 86400}d "
              f"{(data.get('uptime', 0) % 86400) // 3600}h")
        mem_total = data.get('memory', {}).get('total', 0) if isinstance(data.get('memory'), dict) else data.get('maxmem', 0)
        mem_used = data.get('memory', {}).get('used', 0) if isinstance(data.get('memory'), dict) else data.get('mem', 0)
        disk_total = data.get('rootfs', {}).get('total', 0) if isinstance(data.get('rootfs'), dict) else data.get('maxdisk', 0)
        disk_used = data.get('rootfs', {}).get('used', 0) if isinstance(data.get('rootfs'), dict) else data.get('disk', 0)
        print(f"Memory:      {mem_used // (1024**3)}G / {mem_total // (1024**3)}G")
        print(f"CPU Usage:   {data.get('cpu', 0) * 100:.1f}%")
        print(f"Disk:        {disk_used // (1024**3)}G / {disk_total // (1024**3)}G")
        load = data.get('loadavg', [])
        if load:
            print(f"Load Avg:    {', '.join(str(round(x, 2)) for x in load[:3])}")
    elif args.status_type == "vm":
        vmid = args.vmid
        data = api_request(config, "GET", f"/nodes/{node}/qemu/{vmid}/status/current")
        if not data:
            return
        print(f"VM {vmid} ({data.get('name', '?')})")
        print(f"Status:      {data.get('status', '?')}")
        print(f"CPU:         {data.get('cpus', '?')} vCPU ({data.get('cpu', 0) * 100:.1f}% used)")
        print(f"Memory:      {data.get('mem', 0) // (1024**2)} MB / {data.get('maxmem', 0) // (1024**2)} MB")
        print(f"Uptime:      {data.get('uptime', 0) // 3600}h")
        print(f"Disk:        {data.get('disk', 0) // (1024**2)} MB")
        net_in = data.get('netin', 0)
        net_out = data.get('netout', 0)
        print(f"Network:     IN: {net_in // (1024**2)} MB  OUT: {net_out // (1024**2)} MB")
    elif args.status_type == "ct":
        vmid = args.vmid
        data = api_request(config, "GET", f"/nodes/{node}/lxc/{vmid}/status/current")
        if not data:
            return
        print(f"Container {vmid} ({data.get('name', '?')})")
        print(f"Status:      {data.get('status', '?')}")
        print(f"CPU:         {data.get('cpus', '?')} cores")
        print(f"Memory:      {data.get('mem', 0) // (1024**2)} MB / {data.get('maxmem', 0) // (1024**2)} MB")
        print(f"Swap:        {data.get('swap', 0) // (1024**2)} MB / {data.get('maxswap', 0) // (1024**2)} MB")
        print(f"Uptime:      {data.get('uptime', 0) // 3600}h")
        print(f"Disk:        {data.get('disk', 0) // (1024**2)} MB")


def cmd_create(args, config):
    node = config["node"]
    vmid = args.vmid or get_next_vmid(config)
    
    if args.create_type == "ct":
        # Find matching template — search default storage, then fall back to all storages
        templates = get_storage_content(config, "vztmpl")
        if not templates:
            # Fallback: search all storages with vztmpl content
            try:
                storages = api_request(config, "GET", f"/nodes/{config['node']}/storage")
                if storages:
                    for storage in storages:
                        if "vztmpl" in storage.get("content", ""):
                            storage_templates = api_request(config, "GET", f"/nodes/{config['node']}/storage/{storage['storage']}/content", params={"content": "vztmpl"})
                            if storage_templates:
                                templates = storage_templates
                                break
            except Exception:
                pass
        
        if args.template:
            match = [t for t in (templates or []) if args.template.lower() in t.get("volid", "").lower()]
            if not match:
                print(f"ERROR: No template matching '{args.template}' found.")
                available = [t.get("volid", "") for t in (templates or [])]
                print(f"Available templates: {', '.join(available[:10])}")
                return
            ostemplate = match[0]["volid"]
        else:
            if not templates:
                print("ERROR: No templates available. Download one first.")
                return
            # Default to the first Ubuntu or Debian template
            preferred = [t for t in templates if "ubuntu" in t.get("volid", "").lower()]
            if not preferred:
                preferred = [t for t in templates if "debian" in t.get("volid", "").lower()]
            if not preferred:
                preferred = templates
            ostemplate = preferred[0]["volid"]
        
        # Network: detect gateway from node's vmbr0 if not specified
        gateway = args.gateway
        if not gateway and args.ip:
            try:
                networks = api_request(config, "GET", f"/nodes/{config['node']}/network")
                if networks:
                    for iface in networks:
                        if iface.get("iface") == config.get("bridge", "vmbr0"):
                            gateway = iface.get("address")
                            break
            except Exception:
                pass
        
        net0 = f"name=eth0,bridge={config['bridge']},ip=dhcp"
        if args.ip:
            net0 = f"name=eth0,bridge={config['bridge']},ip={args.ip}"
            if gateway:
                net0 += f",gw={gateway}"
        
        payload = {
            "vmid": vmid,
            "ostemplate": ostemplate,
            "storage": config["storage"],
            "rootfs": f"{config['storage']}:{args.disk}",
            "memory": args.memory,
            "cores": args.cores,
            "hostname": args.hostname or f"ct-{vmid}",
            "net0": net0,
            "start": 1,
            "unprivileged": 1,
            "features": "nesting=1",  # Required for Docker-in-LXC
        }
        if args.password:
            payload["password"] = args.password
        
        print(f"Creating container {vmid} ({payload['hostname']})...")
        upid = api_request(config, "POST", f"/nodes/{node}/lxc", data=payload)
        if upid:
            poll_task(config, node, upid, f"Container {vmid} creation")
            print(f"Container {vmid} ({payload['hostname']}) created and started successfully.")
            print(f"Config: {args.memory}MB RAM, {args.cores} vCPU, {args.disk}G disk")
            print(f"Template: {ostemplate}")
            print(f"Network: {net0}")
    else:
        # Create VM
        payload = {
            "vmid": vmid,
            "name": args.name or f"vm-{vmid}",
            "memory": args.memory,
            "cores": args.cores,
            "sockets": 1,
            "cpu": "host",
            "ostype": args.ostype or "l26",
            "net0": f"virtio,bridge={config['bridge']}",
            "scsi0": f"{config['storage']}:{args.disk},format=qcow2",
            "scsihw": "virtio-scsi-pci",
            "agent": 1,
            "start": 1,
        }
        
        print(f"Creating VM {vmid} ({payload['name']})...")
        upid = api_request(config, "POST", f"/nodes/{node}/qemu", data=payload)
        if upid:
            poll_task(config, node, upid, f"VM {vmid} creation")
            print(f"VM {vmid} ({payload['name']}) created and started successfully.")
            print(f"Config: {args.memory}MB RAM, {args.cores} vCPU, {args.disk}G disk")
            print("QEMU Guest Agent enabled (agent=1)")


def cmd_config(args, config):
    node = config["node"]
    payload = {}
    for kv in args.pairs:
        if "=" not in kv:
            print(f"ERROR: Invalid config pair '{kv}'. Use key=value format.")
            return
        key, value = kv.split("=", 1)
        payload[key] = value
    
    endpoint = f"/nodes/{node}/qemu/{args.vmid}/config" if args.config_type == "vm" else f"/nodes/{node}/lxc/{args.vmid}/config"
    print(f"Updating configuration for {args.config_type.upper()} {args.vmid}...")
    result = api_request(config, "PUT", endpoint, data=payload)
    print("Configuration updated.")


def cmd_resize(args, config):
    node = config["node"]
    if args.resize_type == "vm":
        endpoint = f"/nodes/{node}/qemu/{args.vmid}/resize"
        payload = {"disk": args.target, "size": args.size}
    else:
        endpoint = f"/nodes/{node}/lxc/{args.vmid}/resize"
        payload = {"mp": args.target, "size": args.size}
    
    result = api_request(config, "POST", endpoint, data=payload)
    if isinstance(result, str):
        poll_task(config, node, result, "Resize")
    print(f"Disk {args.target} resized by {args.size}.")


def cmd_power(args, config, action):
    node = config["node"]
    # Determine if it's a VM or CT by checking both endpoints
    vm_check = api_request(config, "GET", f"/nodes/{node}/qemu/{args.vmid}")
    if vm_check is not None and any(r.get("vmid") == args.vmid for r in vm_check):
        endpoint = f"/nodes/{node}/qemu/{args.vmid}/status/{action}"
    else:
        endpoint = f"/nodes/{node}/lxc/{args.vmid}/status/{action}"
    
    result = api_request(config, "POST", endpoint)
    if isinstance(result, str):
        poll_task(config, node, result, f"{action.title()}")
    print(f"{action.title()} command issued for {args.vmid}.")


def cmd_delete(args, config):
    node = config["node"]
    # Determine type
    vm_check = api_request(config, "GET", f"/nodes/{node}/qemu/{args.vmid}")
    if vm_check is not None and any(r.get("vmid") == args.vmid for r in vm_check):
        endpoint = f"/nodes/{node}/qemu/{args.vmid}"
    else:
        endpoint = f"/nodes/{node}/lxc/{args.vmid}"
    
    result = api_request(config, "DELETE", endpoint)
    if isinstance(result, str):
        poll_task(config, node, result, f"Delete {args.vmid}")
    print(f"Deleted {args.vmid}.")


def cmd_exec(args, config):
    node = config["node"]
    
    if args.exec_type == "lxc":
        # Execute command in LXC container
        payload = {"command": args.command}
        result = api_request(config, "POST",
                             f"/nodes/{node}/lxc/{args.vmid}/exec",
                             data=payload)
        if result is None:
            print("No output returned.")
            return
        pid = result.get("pid")
        if pid is None:
            print("ERROR: Could not execute command (no PID returned).")
            return
        # Poll for output
        time.sleep(1)
        for _ in range(30):
            out = api_request(config, "GET",
                              f"/nodes/{node}/lxc/{args.vmid}/exec-status",
                              params={"pid": pid})
            if out is None:
                break
            if out.get("exited", 0) == 1:
                stdout = out.get("out-data", "")
                stderr = out.get("err-data", "")
                if stdout:
                    print(stdout.rstrip())
                if stderr:
                    print(f"STDERR: {stderr.rstrip()}", file=sys.stderr)
                if out.get("exitcode", -1) != 0:
                    print(f"Command exited with code {out.get('exitcode')}")
                return
            time.sleep(1)
        print("ERROR: Timed out waiting for command output.")
    else:
        # Execute command in VM via QEMU Guest Agent
        payload = {"command": args.command}
        result = api_request(config, "POST",
                             f"/nodes/{node}/qemu/{args.vmid}/agent/exec",
                             data=payload)
        if result is None:
            return
        pid = result.get("pid")
        if pid is None:
            print("ERROR: QEMU Guest Agent may not be running. Ensure agent=1 is set and qemu-guest-agent is installed inside the VM.")
            return
        time.sleep(2)
        for _ in range(30):
            out = api_request(config, "GET",
                              f"/nodes/{node}/qemu/{args.vmid}/agent/exec-status",
                              params={"pid": pid})
            if out is None:
                break
            if out.get("exited", 0) == 1:
                stdout = out.get("out-data", "")
                stderr = out.get("err-data", "")
                if stdout:
                    print(stdout.rstrip())
                if stderr:
                    print(f"STDERR: {stderr.rstrip()}", file=sys.stderr)
                if out.get("exitcode", -1) != 0:
                    print(f"Command exited with code {out.get('exitcode')}")
                return
            time.sleep(1)
        print("ERROR: Timed out waiting for command output.")


def cmd_log(args, config):
    node = config["node"]
    tasks = api_request(config, "GET", f"/nodes/{node}/tasks",
                        params={"vmid": args.vmid, "limit": 10})
    if not tasks:
        print(f"No tasks found for VM/CT {args.vmid}.")
        return
    print(f"Recent tasks for {args.vmid}:")
    for t in sorted(tasks, key=lambda x: x.get("starttime", 0), reverse=True):
        print(f"  [{t.get('status', '?')}] {t.get('type', '?')} - "
              f"{t.get('user', '?')} - {t.get('exitstatus', 'running')}")
        if t.get("upid"):
            encoded = urllib.parse.quote(t["upid"], safe="")
            log = api_request(config, "GET",
                              f"/nodes/{node}/tasks/{encoded}/log",
                              params={"limit": 5})
            if log:
                for entry in log[-5:]:
                    print(f"    {entry.get('t', '')}")


def cmd_tasks(args, config):
    node = config["node"]
    tasks = api_request(config, "GET", f"/nodes/{node}/tasks", params={"limit": 20})
    if not tasks:
        print("No recent tasks.")
        return
    print(f"{'UPID':<70} {'TYPE':<12} {'STATUS':<12} {'EXIT':<12}")
    print("-" * 120)
    for t in sorted(tasks, key=lambda x: x.get("starttime", 0), reverse=True)[:20]:
        upid_short = t.get("upid", "?")[-40:]
        print(f"{upid_short:<70} {t.get('type', '?'):<12} "
              f"{t.get('status', '?'):<12} {t.get('exitstatus', '?'):<12}")


def cmd_validate(args, config):
    """Validate config and test API connectivity."""
    host = config["host"].rstrip("/")
    headers = {"Authorization": f"PVEAPIToken={config['token_id']}={config['token_secret']}"}
    verify = config["verify_ssl"]

    # Test version endpoint
    try:
        resp = requests.get(f"{host}/api2/json/version", headers=headers, verify=verify, timeout=15)
        if resp.status_code == 401:
            print("VALIDATION FAILED: Invalid API token")
            sys.exit(1)
        if resp.status_code == 403:
            print("VALIDATION FAILED: Permission denied")
            sys.exit(1)
        if resp.status_code >= 400:
            print(f"VALIDATION FAILED: HTTP {resp.status_code}")
            sys.exit(1)
        pve_version = resp.json().get("data", {}).get("version", "unknown")
    except requests.exceptions.SSLError:
        print("VALIDATION FAILED: SSL verification failed. Set verify_ssl to false.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"VALIDATION FAILED: Cannot connect to {host}: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"VALIDATION FAILED: Connection timed out")
        sys.exit(1)

    # Test node exists
    resp = requests.get(f"{host}/api2/json/nodes", headers=headers, verify=verify, timeout=15)
    nodes = resp.json().get("data", [])
    node_names = [n.get("node") for n in nodes]
    if config["node"] not in node_names:
        print(f"VALIDATION FAILED: Node '{config['node']}' not found. Available: {', '.join(node_names)}")
        sys.exit(1)

    print(f"VALIDATION OK: PVE {pve_version} on node '{config['node']}'")


def cmd_ssh(args, config):
    """Execute command via SSH fallback."""
    vmid = args.vmid
    command = args.command

    # Load SSH credentials
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "ssh-credentials.json")

    if not os.path.exists(creds_path):
        print("ERROR: No SSH credentials file found.")
        print("I need SSH credentials to execute commands via SSH.")
        print("Please provide: IP, username, and password for the target container/VM.")
        sys.exit(1)

    with open(creds_path) as f:
        creds_data = json.load(f)

    credentials = creds_data.get("credentials", [])
    cred = None
    for c in credentials:
        if c.get("vmid") == vmid:
            cred = c
            break

    if not cred:
        print(f"ERROR: No SSH credentials found for VMID {vmid}.")
        print("Please provide credentials for this container/VM.")
        sys.exit(1)

    ip = cred["ip"]
    user = cred.get("user", "root")
    password = cred["password"]

    # Check sshpass
    try:
        subprocess.run(["which", "sshpass"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("ERROR: 'sshpass' is required for SSH fallback. Install with: apt-get install -y sshpass")
        sys.exit(1)

    # Execute via SSH
    print(f"Executing via SSH on {cred.get('name', vmid)} ({ip})...")
    result = subprocess.run(
        ["sshpass", "-p", password, "ssh",
         "-o", "ConnectTimeout=10",
         "-o", "StrictHostKeyChecking=no",
         f"{user}@{ip}",
         command],
        capture_output=True, text=True, timeout=60
    )

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(f"STDERR: {result.stderr.rstrip()}", file=sys.stderr)
    if result.returncode != 0:
        print(f"Command exited with code {result.returncode}")
        sys.exit(result.returncode)


def cmd_cache(args, config):
    """View cached discovery data."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, "proxmox-discovery.json")
    
    if not os.path.exists(cache_path):
        print("ERROR: No cache found. Run 'discover' command first.")
        sys.exit(1)
    
    try:
        with open(cache_path) as f:
            cache = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid cache file: {e}")
        sys.exit(1)
    
    # Print cache summary
    discovered_time = time.ctime(cache.get("discovered_at", 0))
    print(f"Proxmox Discovery Cache")
    print(f"=======================")
    print(f"Last updated: {discovered_time}")
    print(f"Node: {cache.get('node', 'unknown')}")
    print()
    
    # Show summary counts
    print("Summary:")
    print(f"  Storages: {len(cache.get('storages', []))}")
    print(f"  VMs: {len(cache.get('vms', []))}")
    print(f"  Containers: {len(cache.get('containers', []))}")
    print(f"  Users: {len(cache.get('users', []))}")
    print(f"  API Tokens: {len(cache.get('api_tokens', []))}")
    print(f"  Pools: {len(cache.get('pools', []))}")
    print(f"  Networks: {len(cache.get('networks', []))}")
    print(f"  SDN Zones: {len(cache.get('sdn_zones', []))}")
    print(f"  SDN VNets: {len(cache.get('sdn_vnets', []))}")
    print()
    
    # If user wants specific category, show details
    if hasattr(args, 'category') and args.category:
        category = args.category.lower()
        if category in cache:
            print(f"{category.upper()} DETAILS:")
            print("-" * 40)
            data = cache[category]
            if isinstance(data, list):
                for i, item in enumerate(data[:10]):  # Show first 10 items
                    if isinstance(item, dict):
                        # Try to show a meaningful identifier
                        name = item.get('name') or item.get('hostname') or item.get('volid') or item.get('userid') or item.get('poolid') or item.get('vmid') or f"item-{i}"
                        print(f"  {name}")
                    else:
                        print(f"  {item}")
                if len(data) > 10:
                    print(f"  ... and {len(data) - 10} more")
            else:
                print(json.dumps(data, indent=2, default=str))
        else:
            print(f"ERROR: Unknown category '{category}'")
            print(f"Available categories: {', '.join([k for k in cache.keys() if k != 'discovered_at'])}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Proxmox VE API CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # list
    p_list = sub.add_parser("list")
    p_list.add_argument("list_type", choices=["vms", "containers", "templates", "isos"])
    p_list.add_argument("--storage", help="Storage to query for templates/isos (default: config storage)")
    
    # status
    p_status = sub.add_parser("status")
    p_status.add_argument("status_type", choices=["node", "vm", "ct"])
    p_status.add_argument("vmid", nargs="?", type=int, help="VM/CT ID (required for vm/ct)")
    
    # create
    p_create = sub.add_parser("create")
    p_create.add_argument("create_type", choices=["vm", "ct"])
    p_create.add_argument("--vmid", type=int, help="VM/CT ID (auto if omitted)")
    p_create.add_argument("--name", help="VM name (VM only)")
    p_create.add_argument("--hostname", help="Container hostname (CT only)")
    p_create.add_argument("--memory", type=int, default=1024, help="Memory in MB")
    p_create.add_argument("--cores", type=int, default=1, help="Number of CPU cores")
    p_create.add_argument("--disk", type=int, default=8, help="Disk size in GB")
    p_create.add_argument("--template", help="Container template name (CT only, partial match)")
    p_create.add_argument("--ostype", default="l26", help="OS type for VM (e.g., l26, win10)")
    p_create.add_argument("--password", help="Root password (CT only)")
    p_create.add_argument("--ip", help="Static IP with CIDR, e.g. 192.168.1.104/24 (CT only)")
    p_create.add_argument("--gateway", help="Gateway IP (defaults to node vmbr0 IP) (CT only)")
    
    # config
    p_config = sub.add_parser("config")
    p_config.add_argument("config_type", choices=["vm", "ct"])
    p_config.add_argument("vmid", type=int)
    p_config.add_argument("pairs", nargs="+", help="key=value pairs")
    
    # resize
    p_resize = sub.add_parser("resize")
    p_resize.add_argument("resize_type", choices=["vm", "ct"])
    p_resize.add_argument("vmid", type=int)
    p_resize.add_argument("target", help="Disk name (e.g., scsi0) or mount point (e.g., rootfs)")
    p_resize.add_argument("size", help="Size change (e.g., +10G)")
    
    # power
    for action in ("start", "stop", "shutdown", "reboot"):
        p = sub.add_parser(action)
        p.add_argument("vmid", type=int)
    
    # delete
    p_del = sub.add_parser("delete")
    p_del.add_argument("vmid", type=int)
    
    # exec
    p_exec = sub.add_parser("exec")
    p_exec.add_argument("exec_type", choices=["lxc", "qemu"])
    p_exec.add_argument("vmid", type=int)
    p_exec.add_argument("command", nargs="+", help="Command and arguments")
    
    # log
    p_log = sub.add_parser("log")
    p_log.add_argument("vmid", type=int)
    
    # tasks
    sub.add_parser("tasks")

    # discover
    sub.add_parser("discover", help="Discover and cache server information (storages, VMs, containers, users, tokens, pools, networks, SDN)")

    # cache
    p_cache = sub.add_parser("cache", help="View cached discovery data")
    p_cache.add_argument("category", nargs="?", help="Category to view (storages, vms, containers, users, api_tokens, pools, networks, sdn_zones, sdn_vnets)")

    # validate
    sub.add_parser("validate", help="Validate config and test API connectivity")

    # ssh
    p_ssh = sub.add_parser("ssh", help="Execute command via SSH fallback")
    p_ssh.add_argument("vmid", type=int, help="VM/CT ID")
    p_ssh.add_argument("command", nargs="+", help="Command and arguments")

    args = parser.parse_args()
    config = load_config()

    if args.command == "list":
        cmd_list(args, config)
    elif args.command == "status":
        if args.status_type in ("vm", "ct") and args.vmid is None:
            print("ERROR: vmid is required for vm/ct status.")
            sys.exit(1)
        cmd_status(args, config)
    elif args.command == "create":
        if args.create_type == "ct" and args.password is None:
            print("WARNING: No password set for container. Setting default 'proxmox!'")
            args.password = "proxmox!"
        cmd_create(args, config)
    elif args.command == "config":
        if not args.pairs:
            print("ERROR: At least one key=value pair is required.")
            sys.exit(1)
        cmd_config(args, config)
    elif args.command == "resize":
        cmd_resize(args, config)
    elif args.command in ("start", "stop", "shutdown", "reboot"):
        cmd_power(args, config, args.command)
    elif args.command == "delete":
        cmd_delete(args, config)
    elif args.command == "exec":
        args.command = " ".join(args.command)
        cmd_exec(args, config)
    elif args.command == "log":
        cmd_log(args, config)
    elif args.command == "tasks":
        cmd_tasks(args, config)
    elif args.command == "discover":
        discover_and_cache(config)
    elif args.command == "cache":
        cmd_cache(args, config)
    elif args.command == "validate":
        cmd_validate(args, config)
    elif args.command == "ssh":
        args.command = " ".join(args.command)
        cmd_ssh(args, config)

if __name__ == "__main__":
    main()
