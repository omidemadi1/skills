#!/usr/bin/env python3
"""
Proxmox VE config validator.

Tests connectivity and API token validity by making a real API call.

Usage:
    python proxmox_validate.py
    python proxmox_validate.py --config /path/to/config.json
"""
import json
import os
import sys

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


def load_config(config_path=None):
    if config_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "proxmox-config.json")

    if not os.path.exists(config_path):
        return None, f"Config file not found: {config_path}"

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in config file: {e}"

    required = ["host", "token_id", "token_secret", "node"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        return None, f"Missing required fields: {', '.join(missing)}"

    return config, None


def validate_connection(config):
    host = config["host"].rstrip("/")
    token_id = config["token_id"]
    token_secret = config["token_secret"]
    node = config["node"]
    verify_ssl = config.get("verify_ssl", False)

    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}"
    }

    # Test 1: Basic connectivity + version
    try:
        resp = requests.get(
            f"{host}/api2/json/version",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        if resp.status_code == 401:
            return False, "Authentication failed: Invalid API token"
        if resp.status_code == 403:
            return False, "Permission denied: API token lacks required permissions"
        if resp.status_code >= 400:
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        version_data = resp.json().get("data", {})
        pve_version = version_data.get("version", "unknown")
    except requests.exceptions.SSLError:
        return False, "SSL verification failed. Set verify_ssl to false or fix certificates."
    except requests.exceptions.ConnectionError as e:
        return False, f"Cannot connect to {host}: {e}"
    except requests.exceptions.Timeout:
        return False, f"Connection timed out to {host}"

    # Test 2: Node exists
    try:
        resp = requests.get(
            f"{host}/api2/json/nodes",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        nodes = resp.json().get("data", [])
        node_names = [n.get("node") for n in nodes]
        if node not in node_names:
            return False, f"Node '{node}' not found. Available nodes: {', '.join(node_names)}"
    except Exception as e:
        return False, f"Failed to list nodes: {e}"

    # Test 3: VM listing permission
    try:
        resp = requests.get(
            f"{host}/api2/json/nodes/{node}/qemu",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        if resp.status_code == 403:
            return False, "Permission denied: Cannot list VMs (need VM.Audit)"
    except Exception:
        pass

    # Test 4: Container listing permission
    try:
        resp = requests.get(
            f"{host}/api2/json/nodes/{node}/lxc",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        if resp.status_code == 403:
            return False, "Permission denied: Cannot list containers (need VM.Audit)"
    except Exception:
        pass

    return True, f"Connected to PVE {pve_version} on node '{node}'"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate Proxmox VE config")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    config, error = load_config(args.config)
    if error:
        print(f"VALIDATION FAILED: {error}")
        sys.exit(1)

    success, message = validate_connection(config)
    if success:
        print(f"VALIDATION OK: {message}")
        sys.exit(0)
    else:
        print(f"VALIDATION FAILED: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
