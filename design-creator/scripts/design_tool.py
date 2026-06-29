import sys, json, os, re

DESIGN_MD = "Design.md"

def _read_md():
    if not os.path.exists(DESIGN_MD):
        return None
    with open(DESIGN_MD, "r") as f:
        return f.read()

def _write_md(content):
    with open(DESIGN_MD, "w") as f:
        f.write(content)

def cmd_check(name):
    content = _read_md()
    if content is None:
        print(json.dumps({"exists": False, "reason": "Design.md not found"}))
        return
    pattern = re.compile(r"^###\s+" + re.escape(name.strip()) + r"\s*$", re.MULTILINE)
    match = pattern.search(content)
    if match:
        print(json.dumps({"exists": True}))
    else:
        print(json.dumps({"exists": False, "reason": f"Component '{name}' not found in Design.md"}))

def cmd_get_tokens():
    content = _read_md()
    if content is None:
        print(json.dumps({"error": "Design.md not found"}))
        return
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        try:
            tokens = json.loads(match.group(1))
            print(json.dumps(tokens))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Failed to parse tokens JSON: {str(e)}"}))
    else:
        print(json.dumps({"error": "No design tokens JSON block found in Design.md"}))

def cmd_list_components():
    content = _read_md()
    if content is None:
        print(json.dumps({"components": []}))
        return
    components = re.findall(r"^###\s+(.+?)\s*$", content, re.MULTILINE)
    print(json.dumps({"components": components}))

def cmd_append(data_str):
    content = _read_md()
    if content is None:
        print(json.dumps({"success": False, "error": "Design.md not found. Create it first."}))
        return
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"}))
        return

    name = data.get("name", "").strip()
    if not name:
        print(json.dumps({"success": False, "error": "Component name is required"}))
        return

    existing_check = _read_md()
    if re.search(r"^###\s+" + re.escape(name) + r"\s*$", existing_check, re.MULTILINE):
        print(json.dumps({"success": False, "error": f"Component '{name}' already exists"}))
        return

    section = "\n\n### " + name + "\n"
    props = data.get("properties", {})
    if props:
        for key, value in props.items():
            section += f"- **{key}**: {value}\n"

    states = data.get("states", {})
    if states:
        section += "\n**States:**\n"
        for state, desc in states.items():
            section += f"- *{state}*: {desc}\n"

    notes = data.get("notes", "")
    if notes:
        section += "\n**Notes:** " + notes + "\n"

    _write_md(existing_check + section)
    print(json.dumps({"success": True, "component": name}))

def cmd_init(data_str):
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"}))
        return

    name = data.get("product_name", "My Product")
    tokens = data.get("tokens", {})
    sections = data.get("sections", [])

    md = f"# Design System: {name}\n\n"
    md += "## Design Tokens\n```json\n"
    md += json.dumps(tokens, indent=2)
    md += "\n```\n\n"

    for section in sections:
        title = section.get("title", "")
        body = section.get("body", "")
        md += f"## {title}\n{body}\n\n"

    _write_md(md)
    print(json.dumps({"success": True, "file": DESIGN_MD}))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: design_tool.py <check|get_tokens|list_components|append|init> [args]"}))
        sys.exit(1)

    command = sys.argv[1]
    if command == "check":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: design_tool.py check <component_name>"}))
            sys.exit(1)
        cmd_check(sys.argv[2])
    elif command == "get_tokens":
        cmd_get_tokens()
    elif command == "list_components":
        cmd_list_components()
    elif command == "append":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: design_tool.py append <json_string>"}))
            sys.exit(1)
        cmd_append(sys.argv[2])
    elif command == "init":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: design_tool.py init <json_string>"}))
            sys.exit(1)
        cmd_init(sys.argv[2])
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)
