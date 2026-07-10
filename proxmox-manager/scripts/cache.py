#!/usr/bin/env python3
"""
Utility to view cached Proxmox discovery data.
"""

import json
import os
import sys
from datetime import datetime

def load_cache():
    """Load cached discovery data."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, "proxmox-discovery.json")
    
    if not os.path.exists(cache_path):
        print("Cache file not found. Run 'python proxmox_api.py discover' first.")
        return None
    
    try:
        with open(cache_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading cache: {e}")
        return None

def view_storages(cache):
    """View storage information."""
    print("=== STORAGES ===")
    for storage in cache.get("storages", []):
        print(f"ID: {storage.get('storage')}")
        print(f"  Type: {storage.get('type')}")
        print(f"  Content: {storage.get('content')}")
        print(f"  Enabled: {storage.get('enabled')}")
        print(f"  Shared: {storage.get('shared')}")
        if storage.get('total'):
            total_gb = int(storage['total']) // (1024**3)
            used_gb = int(storage.get('used', 0)) // (1024**3)
            print(f"  Capacity: {used_gb}G / {total_gb}G")
        print()

def view_vms(cache):
    """View VM information."""
    print("=== VIRTUAL MACHINES ===")
    for vm in cache.get("vms", []):
        vmid = vm.get('vmid', '?')
        name = vm.get('name', 'unnamed')
        status = vm.get('status', '?')
        print(f"VM {vmid}: {name} [{status}]")
        if 'detailed_config' in vm:
            config = vm['detailed_config']
            memory_mb = config.get('memory', 0) // 1024
            cores = config.get('cores', 1)
            print(f"  Config: {memory_mb}MB RAM, {cores} vCPU")
            if config.get('net0'):
                print(f"  Network: {config['net0']}")
        if 'detailed_status' in vm:
            status_data = vm['detailed_status']
            uptime_h = status_data.get('uptime', 0) // 3600
            cpu_pct = status_data.get('cpu', 0) * 100
            mem_mb = status_data.get('mem', 0) // (1024**2)
            maxmem_mb = status_data.get('maxmem', 0) // (1024**2)
            print(f"  Status: {uptime_h}h uptime, {cpu_pct:.1f}% CPU, {mem_mb}G/{maxmem_mb}G RAM")
        print()

def view_containers(cache):
    """View container information."""
    print("=== CONTAINERS (LXC) ===")
    for ct in cache.get("containers", []):
        vmid = ct.get('vmid', '?')
        hostname = ct.get('hostname', 'unnamed')
        status = ct.get('status', '?')
        print(f"CT {vmid}: {hostname} [{status}]")
        if 'detailed_config' in ct:
            config = ct['detailed_config']
            memory_mb = config.get('memory', 0) // 1024
            cores = config.get('cores', 1)
            swap_mb = config.get('swap', 0) // 1024
            print(f"  Config: {memory_mb}MB RAM, {cores} cores, {swap_mb}MB swap")
            if config.get('net0'):
                print(f"  Network: {config['net0']}")
        if 'detailed_status' in ct:
            status_data = ct['detailed_status']
            uptime_h = status_data.get('uptime', 0) // 3600
            cpu_pct = status_data.get('cpu', 0) * 100
            mem_mb = status_data.get('mem', 0) // (1024**2)
            maxmem_mb = status_data.get('maxmem', 0) // (1024**2)
            swap_mb = status_data.get('swap', 0) // (1024**2)
            maxswap_mb = status_data.get('maxswap', 0) // (1024**2)
            print(f"  Status: {uptime_h}h uptime, {cpu_pct:.1f}% CPU, {mem_mb}G/{maxmem_mb}G RAM, {swap_mb}G/{maxswap_mb}G swap")
        print()

def view_users(cache):
    """View user information."""
    print("=== USERS ===")
    for user in cache.get("users", []):
        userid = user.get('userid', 'unknown')
        firstname = user.get('firstname', '')
        lastname = user.get('lastname', '')
        email = user.get('email', '')
        enabled = user.get('enable', 0)
        print(f"User: {userid}")
        if firstname or lastname:
            print(f"  Name: {firstname} {lastname}".strip())
        if email:
            print(f"  Email: {email}")
        print(f"  Enabled: {'Yes' if enabled else 'No'}")
        print(f"  Groups: {', '.join(user.get('groups', []))}")
        print()

def view_tokens(cache):
    """View API token information."""
    print("=== API TOKENS ===")
    for token in cache.get("api_tokens", []):
        tokenid = token.get('tokenid', 'unknown')
        userid = token.get('userid', 'unknown')
        print(f"Token: {tokenid}")
        print(f"  User: {userid}")
        print(f"  Description: {token.get('description', '')}")
        print(f"  Expires: {token.get('expire', 0)} (epoch)")
        print(f"  Privileges: {token.get('privs', '')}")
        print()

def view_pools(cache):
    """View resource pools."""
    print("=== RESOURCE POOLS ===")
    for pool in cache.get("pools", []):
        poolid = pool.get('poolid', 'unknown')
        print(f"Pool: {poolid}")
        print(f"  Comment: {pool.get('comment', '')}")
        members = pool.get('members', [])
        if members:
            print(f"  Members ({len(members)}):")
            for member in members[:5]:  # Show first 5
                print(f"    - {member.get('type', '?')}/{member.get('vmid', '?')}")
            if len(members) > 5:
                print(f"    ... and {len(members) - 5} more")
        print()

def view_networks(cache):
    """View network interfaces."""
    print("=== NETWORK INTERFACES ===")
    for net in cache.get("networks", []):
        iface = net.get('iface', 'unknown')
        print(f"Interface: {iface}")
        print(f"  Type: {net.get('type', 'unknown')}")
        print(f"  Comment: {net.get('comment', '')}")
        # Show key-value pairs for common fields
        for key in ['address', 'cidr', 'gateway', 'mtu', 'vlan']:
            if net.get(key):
                print(f"  {key.capitalize()}: {net[key]}")
        print()

def view_sdn_zones(cache):
    """View SDN zones."""
    print("=== SDN ZONES ===")
    for zone in cache.get("sdn_zones", []):
        zoneid = zone.get('zone', 'unknown')
        print(f"Zone: {zoneid}")
        print(f"  Type: {zone.get('type', 'unknown')}")
        print(f"  DNS Domain: {zone.get('domain', '')}")
        print(f"  MTU: {zone.get('mtu', 'default')}")
        print(f"  Description: {zone.get('description', '')}")
        print()

def view_sdn_vnets(cache):
    """View SDN VNets."""
    print("=== SDN VNETS ===")
    for vnet in cache.get("sdn_vnets", []):
        vnetid = vnet.get('vnet', 'unknown')
        print(f"VNet: {vnetid}")
        print(f"  Zone: {vnet.get('zone', 'unknown')}")
        print(f"  VID: {vnet.get('vid', 'unknown')}")
        print(f"  Description: {vnet.get('description', '')}")
        print()

def main():
    cache = load_cache()
    if not cache:
        return 1
    
    # Show cache timestamp
    discovered_at = cache.get('discovered_at', 0)
    if discovered_at:
        dt = datetime.fromtimestamp(discovered_at)
        print(f"Cache created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Node: {cache.get('node', 'unknown')}")
        print()
    
    # View all sections
    view_storages(cache)
    view_vms(cache)
    view_containers(cache)
    view_users(cache)
    view_tokens(cache)
    view_pools(cache)
    view_networks(cache)
    view_sdn_zones(cache)
    view_sdn_vnets(cache)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())