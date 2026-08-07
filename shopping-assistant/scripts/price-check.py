#!/usr/bin/env python3
"""
Price check script for the shopping assistant.
Reads all project files in ~/projects/shopping/ and extracts
URLs with their recorded prices for price monitoring.

Output is injected into the cron agent's prompt for comparison.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

SHOPPING_DIR = Path.home() / "projects" / "shopping"


def extract_prices_from_md(filepath):
    """Extract product URLs and prices from a project markdown file."""
    content = filepath.read_text(encoding="utf-8")
    
    # Extract project name from first heading
    name_match = re.search(r'^# Project:\s*(.+)$', content, re.MULTILINE)
    project_name = name_match.group(1).strip() if name_match else filepath.stem
    
    # Extract all table rows with links and prices
    # Pattern: | # | item_en | item_fa | specs | price | value | [link](url) | site |
    items = []
    
    # Find all markdown links with their surrounding table row context
    rows = re.findall(
        r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*([\d,]+)\s*(?:تومان)?\s*\|\s*(.+?)\s*\|\s*\[.*?\]\((https?://[^\)]+)\)\s*\|\s*(.+?)\s*\|',
        content
    )
    
    for row in rows:
        num, item_en, item_fa, specs, price, value, url, site = row
        price_clean = int(price.replace(',', ''))
        items.append({
            "item_en": item_en.strip(),
            "item_fa": item_fa.strip(),
            "specs": specs.strip(),
            "price": price_clean,
            "price_formatted": f"{price_clean:,}",
            "url": url.strip(),
            "site": site.strip()
        })
    
    # Extract last price check date
    price_checks = re.findall(r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([\d,]+)', content)
    last_check = price_checks[-1] if price_checks else None
    
    return {
        "project_name": project_name,
        "file": str(filepath),
        "items": items,
        "last_check": last_check,
        "item_count": len(items)
    }


def main():
    if not SHOPPING_DIR.exists():
        print("NO_PROJECTS_FOUND")
        print("No shopping projects exist yet at ~/projects/shopping/")
        return
    
    project_files = list(SHOPPING_DIR.glob("*.md"))
    # Exclude the learnings file
    project_files = [f for f in project_files if f.name != ".learnings.md"]
    
    if not project_files:
        print("NO_PROJECTS_FOUND")
        print("No project files found in ~/projects/shopping/")
        return
    
    projects = []
    for pf in sorted(project_files):
        try:
            project = extract_prices_from_md(pf)
            if project["items"]:
                projects.append(project)
        except Exception as e:
            print(f"ERROR reading {pf.name}: {e}")
    
    if not projects:
        print("NO_TRACKABLE_ITEMS")
        print("Project files exist but contain no trackable items with URLs.")
        return
    
    # Output structured data for the agent
    print("=== SHOPPING PRICE CHECK ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Projects to check: {len(projects)}")
    print()
    
    for project in projects:
        print(f"## {project['project_name']}")
        print(f"File: {project['file']}")
        print(f"Items: {project['item_count']}")
        if project['last_check']:
            print(f"Last check: {project['last_check'][0]}")
        print()
        
        for item in project["items"]:
            print(f"  - {item['item_en']} ({item['item_fa']})")
            print(f"    Specs: {item['specs']}")
            print(f"    Recorded price: {item['price_formatted']} تومان")
            print(f"    URL: {item['url']}")
            print(f"    Site: {item['site']}")
        print()
    
    print("=== INSTRUCTIONS ===")
    print("For each item above, search for the current price on the listed site.")
    print("Compare with the recorded price.")
    print("Report ONLY items where price dropped by 10% or more.")
    print("If no significant drops, output: NO_PRICE_DROPS_DETECTED")
    print("If drops found, format as a clear message with old vs new prices.")


if __name__ == "__main__":
    main()
