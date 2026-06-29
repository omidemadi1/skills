#!/usr/bin/env python3
"""
Test script for program-structure-generator skill.
"""

import json
import subprocess
import sys
import os


def test_parse_description():
    """Test the parse_description script."""
    print("Testing parse_description script...")
    
    test_file = "/root/.mimocode/skills/program-structure-generator/evals/test-descriptions/weather-dashboard.md"
    
    result = subprocess.run(
        ["python3", "/root/.mimocode/skills/program-structure-generator/scripts/parse_description.py", test_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        print(f"Detected languages: {data['detected']['languages']}")
        print(f"Detected frameworks: {data['detected']['frameworks']}")
        print(f"Project name: {data['detected']['project_name']}")
        print("✓ parse_description script works")
        return True
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON output")
        return False


def test_generate_tree():
    """Test the generate_tree script."""
    print("\nTesting generate_tree script...")
    
    test_input = "/root/.mimocode/skills/program-structure-generator/evals/test-tree-input.json"
    
    result = subprocess.run(
        ["python3", "/root/.mimocode/skills/program-structure-generator/scripts/generate_tree.py", test_input],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    output = result.stdout
    if "weather-dashboard/" in output and "├──" in output and "└──" in output:
        print("✓ generate_tree script works")
        print("Sample output:")
        for line in output.split('\n')[:10]:
            print(f"  {line}")
        return True
    else:
        print(f"Error: Unexpected output format")
        return False


def test_end_to_end():
    """Test end-to-end workflow."""
    print("\nTesting end-to-end workflow...")
    
    # Parse description
    test_file = "/root/.mimocode/skills/program-structure-generator/evals/test-descriptions/weather-dashboard.md"
    
    result = subprocess.run(
        ["python3", "/root/.mimocode/skills/program-structure-generator/scripts/parse_description.py", test_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error parsing description: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        detected = data["detected"]
        recommendations = data["recommendations"]
        
        # Create tree input from recommendations
        items = []
        
        # Add directories
        for dir_path in recommendations["directories"]:
            if not dir_path.endswith("/"):
                dir_path += "/"
            items.append({"path": dir_path, "annotation": f"Directory for {dir_path.split('/')[-2]}"})
        
        # Add standard files
        for file_name in recommendations["standard_files"]:
            items.append({"path": file_name, "annotation": f"Standard {file_name} file"})
        
        # Add config files
        for file_name in recommendations["config_files"]:
            items.append({"path": file_name, "annotation": f"Configuration file"})
        
        # Create temporary input file
        temp_input = "/tmp/test_tree_input.json"
        with open(temp_input, 'w') as f:
            json.dump({
                "project_name": detected["project_name"],
                "items": items
            }, f)
        
        # Generate tree
        result = subprocess.run(
            ["python3", "/root/.mimocode/skills/program-structure-generator/scripts/generate_tree.py", temp_input],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error generating tree: {result.stderr}")
            return False
        
        output = result.stdout
        if detected["project_name"] in output:
            print("✓ End-to-end workflow works")
            print(f"Generated structure for: {detected['project_name']}")
            print(f"Contains {len(items)} items")
            return True
        else:
            print(f"Error: Project name not found in output")
            return False
            
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON output")
        return False


def main():
    """Run all tests."""
    print("Running program-structure-generator skill tests...\n")
    
    tests = [
        test_parse_description,
        test_generate_tree,
        test_end_to_end
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())