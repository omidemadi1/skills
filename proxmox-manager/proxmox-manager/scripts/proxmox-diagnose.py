#!/usr/bin/env python3
"""
Proxmox API Connection Diagnostic Tool
Helps verify API token permissions, node name, and resource access.
"""

import json
import os
import sys
import requests
from urllib.parse import quote

def load_config():
    """Load configuration from proxmox-config.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "proxmox-config.json")
    
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Config file not found at {config_path}")
        print("Please create it first or run the proxmox-manager skill setup.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file: {e}")
        sys.exit(1)

def api_request(config, method, path, params=None, data=None):
    """Make an API request to Proxmox"""
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
            verify=config.get("verify_ssl", False),
            timeout=30
        )
    except requests.exceptions.SSLError:
        print("WARNING: SSL verification failed. Consider setting verify_ssl to false or fixing certificates.")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Cannot connect to {config['host']}: {e}")
        return None
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
        return None
    
    if resp.status_code >= 400:
        try:
            err = resp.json()
            msg = err.get("errors", err.get("data", str(err)))
        except Exception:
            msg = resp.text
        print(f"ERROR {resp.status_code}: {msg}")
        return None
    
    return resp.json().get("data")

def test_basic_connectivity(config):
    """Test basic API connectivity"""
    print("=== Testing Basic Connectivity ===")
    version = api_request(config, "GET", "/version")
    if version:
        print(f"✓ Connected to Proxmox VE {version.get('version', 'unknown')}")
        return True
    else:
        print("✗ Failed to connect to Proxmox API")
        return False

def test_node_name(config):
    """Verify the node name in config"""
    print("\n=== Testing Node Name ===")
    nodes = api_request(config, "GET", "/nodes")
    if nodes is None:
        print("✗ Failed to retrieve nodes list")
        return False
    
    node_names = [node["node"] for node in nodes]
    print(f"Available nodes: {', '.join(node_names)}")
    
    if config["node"] in node_names:
        print(f"✓ Node '{config['node']}' found in config")
        return True
    else:
        print(f"✗ Node '{config['node']}' NOT found in available nodes")
        if node_names:
            print(f"  Suggestion: Update config to use one of: {', '.join(node_names)}")
        return False

def test_vm_permissions(config, vmid=105):
    """Test permissions for a specific VMID"""
    print(f"\n=== Testing VM {vmid} Permissions ===")
    
    # Test if it exists as a VM
    vm_data = api_request(config, "GET", f"/nodes/{config['node']}/qemu/{vmid}/config")
    if vm_data is not None:
        print(f"✓ VM {vmid} exists and can be read (VM.Audit permission)")
    else:
        print(f"✗ Cannot read VM {vmid} config (missing VM.Audit or wrong type)")
    
    # Test if it exists as a container
    ct_data = api_request(config, "GET", f"/nodes/{config['node']}/lxc/{vmid}/config")
    if ct_data is not None:
        print(f"✓ Container {vmid} exists and can be read (VM.Audit permission for CT)")
    else:
        print(f"✗ Cannot read container {vmid} config (missing VM.Audit or wrong type)")
    
    # Test power management permission (just check if we can attempt it)
    # We won't actually start it, just see if we get a permission error vs not found
    vm_status = api_request(config, "GET", f"/nodes/{config['node']}/qemu/{vmid}/status/current")
    if vm_status is not None:
        print(f"✓ Can query VM {vmid} status (VM.Audit permission)")
    else:
        # Check if it's a permission error vs not found
        ct_status = api_request(config, "GET", f"/nodes/{config['node']}/lxc/{vmid}/status/current")
        if ct_status is not None:
            print(f"✓ Can query container {vmid} status (VM.Audit permission)")
        else:
            print(f"✗ Cannot query status for VMID {vmid} as either VM or container")

def test_storage_access(config):
    """Test access to storage"""
    print(f"\n=== Testing Storage Access ===")
    storage = config.get("storage", "local-lvm")
    content = api_request(config, "GET", f"/nodes/{config['node']}/storage/{storage}/content")
    if content is not None:
        print(f"✓ Can list storage '{storage}' content (Datastore.Audit permission)")
        # Show first few items as examples
        if content:
            print(f"  Found {len(content)} items (showing first 3):")
            for item in content[:3]:
                volid = item.get('volid', 'unknown')
                print(f"    - {volid}")
        else:
            print(f"  Storage '{storage}' is empty")
    else:
        print(f"✗ Cannot list storage '{storage}' content (missing Datastore.Audit permission)")

def main():
    print("Proxmox API Connection Diagnostic Tool")
    print("=" * 50)
    
    config = load_config()
    
    print(f"Config loaded:")
    print(f"  Host: {config['host']}")
    print(f"  Node: {config['node']}")
    print(f"  Storage: {config.get('storage', 'local-lvm')}")
    print(f"  Bridge: {config.get('bridge', 'vmbr0')}")
    print(f"  Verify SSL: {config.get('verify_ssl', False)}")
    print(f"  Token ID: {config['token_id']}")
    
    # Run tests
    if not test_basic_connectivity(config):
        return 1
    
    if not test_node_name(config):
        return 1
    
    test_vm_permissions(config)
    test_storage_access(config)
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")
    print("If you see permission errors above, refer to:")
    print("  references/permission-debugging.md")
    print("  references/verification-steps.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())