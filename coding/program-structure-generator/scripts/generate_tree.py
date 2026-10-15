#!/usr/bin/env python3
"""
Generate tree structure with annotations for program structure generator.
"""

import json
import sys
from typing import Dict, List, Any


def generate_tree(structure: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
    """
    Generate a tree string from a nested dictionary structure.
    
    Args:
        structure: Nested dictionary representing directory structure
        prefix: Current prefix for tree lines
        is_last: Whether this is the last item in its parent
        
    Returns:
        Formatted tree string
    """
    lines = []
    items = list(structure.items())
    
    for i, (name, info) in enumerate(items):
        is_last_item = (i == len(items) - 1)
        
        if isinstance(info, dict) and "children" in info:
            # Directory
            connector = "└── " if is_last_item else "├── "
            annotation = info.get("annotation", "")
            if annotation:
                lines.append(f"{prefix}{connector}{name:<30}# {annotation}")
            else:
                lines.append(f"{prefix}{connector}{name}")
            
            # Recursively process children
            extension = "    " if is_last_item else "│   "
            child_lines = generate_tree(
                info["children"],
                prefix + extension,
                is_last_item
            )
            lines.append(child_lines)
        else:
            # File
            connector = "└── " if is_last_item else "├── "
            annotation = info.get("annotation", "") if isinstance(info, dict) else ""
            if annotation:
                lines.append(f"{prefix}{connector}{name:<30}# {annotation}")
            else:
                lines.append(f"{prefix}{connector}{name}")
    
    return "\n".join(lines)


def create_structure_from_list(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a nested structure from a flat list of items.
    
    Args:
        items: List of dictionaries with 'path' and 'annotation' keys
        
    Returns:
        Nested dictionary structure
    """
    root = {}
    
    for item in items:
        path = item.get("path", "")
        annotation = item.get("annotation", "")
        
        # Remove leading/trailing slashes and split
        path = path.strip("/")
        if not path:
            continue
            
        parts = path.split("/")
        current = root
        
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            is_directory = path.endswith("/")
            
            if part not in current:
                if is_last and is_directory:
                    # Directory
                    current[part] = {"annotation": annotation, "children": {}}
                elif is_last and not is_directory:
                    # File
                    current[part] = {"annotation": annotation}
                else:
                    # Intermediate directory
                    current[part] = {"annotation": "", "children": {}}
            
            # Move to children if this is a directory
            if isinstance(current[part], dict) and "children" in current[part]:
                current = current[part]["children"]
            elif not is_last:
                # This shouldn't happen, but handle it
                current[part] = {"annotation": "", "children": {}}
                current = current[part]["children"]
    
    return root


def format_tree_output(project_name: str, structure: Dict[str, Any]) -> str:
    """
    Format the complete tree output with project name.
    
    Args:
        project_name: Name of the project
        structure: Nested structure dictionary
        
    Returns:
        Complete formatted tree string
    """
    lines = [f"{project_name}/"]
    tree_lines = generate_tree(structure)
    lines.append(tree_lines)
    return "\n".join(lines)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: generate_tree.py <json_file>")
        print("  or: echo '<json>' | generate_tree.py -")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # Read from stdin
        data = json.load(sys.stdin)
    else:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    
    project_name = data.get("project_name", "project")
    items = data.get("items", [])
    
    structure = create_structure_from_list(items)
    output = format_tree_output(project_name, structure)
    print(output)


if __name__ == "__main__":
    main()