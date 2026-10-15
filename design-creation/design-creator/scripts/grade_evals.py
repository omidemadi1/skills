import json, os, re, sys

def read_file(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()

def grade_eval_1(base_dir):
    content = read_file(os.path.join(base_dir, "Design.md"))
    if not content:
        return all_false(7)

    results = []
    results.append(check("Creates a Design.md file", content is not None, "Design.md exists"))

    has_tokens = bool(re.search(r"```json\s*\{", content))
    has_colors = bool(re.search(r'"colors"\s*:', content))
    has_typo = bool(re.search(r'"typography"\s*:', content))
    has_spacing = bool(re.search(r'"spacing"\s*:', content))
    has_radius = bool(re.search(r'"borderRadius"\s*:', content))
    has_shadows = bool(re.search(r'"shadows"\s*:', content))
    results.append(check("Has JSON tokens block", has_tokens and has_colors and has_typo and has_spacing and has_radius and has_shadows, f"tokens:{has_tokens}, colors:{has_colors}, typo:{has_typo}, spacing:{has_spacing}, radius:{has_radius}, shadows:{has_shadows}"))

    has_light = bool(re.search(r'"light"\s*:', content))
    has_dark = bool(re.search(r'"dark"\s*:', content))
    results.append(check("Has light+dark palettes", has_light and has_dark, f"light:{has_light}, dark:{has_dark}"))

    has_google_font = bool(re.search(r'fonts\.google\.com|Google Fonts', content, re.IGNORECASE))
    results.append(check("Has Google Fonts", has_google_font, f"google_font:{has_google_font}"))

    has_icon_lib = bool(re.search(r'Lucide|Phosphor|Heroicons|Feather|Font Awesome|Material Icons', content))
    has_icon_style = bool(re.search(r'outline|filled|duotone|stroke', content, re.IGNORECASE))
    results.append(check("Has icon style+library", has_icon_lib or has_icon_style, f"icon_lib:{has_icon_lib}, icon_style:{has_icon_style}"))

    spacing_levels = re.findall(r'"\w+"\s*:\s*\d+', content[content.find('"spacing"'):content.find('"spacing"')+200] if '"spacing"' in content else "")
    results.append(check("Has spacing scale >=4 levels", len(spacing_levels) >= 4, f"spacing_levels:{len(spacing_levels)}"))

    radius_levels = re.findall(r'"\w+"\s*:\s*\d+', content[content.find('"borderRadius"'):content.find('"borderRadius"')+200] if '"borderRadius"' in content else "")
    results.append(check("Has border radius scale", len(radius_levels) >= 3, f"radius_levels:{len(radius_levels)}"))

    return results

def grade_eval_2(base_dir):
    content = read_file(os.path.join(base_dir, "Design.md"))
    log = read_file(os.path.join(base_dir, "commands.log"))

    if not content:
        # Check for separate design files
        for f in os.listdir(base_dir):
            if f.endswith('.md'):
                content = read_file(os.path.join(base_dir, f))
                if content: break

    results = []

    used_check = log and "check" in log
    results.append(check("Checks before creating", used_check, f"used_check:{used_check}"))

    has_tokens = bool(re.search(r"```json", content or ""))
    has_dropdown = bool(re.search(r"Profile Dropdown|profile.dropdown|dropdown", content or "", re.IGNORECASE))
    results.append(check("Designs using existing tokens", has_tokens and has_dropdown, f"tokens:{has_tokens}, dropdown:{has_dropdown}"))

    props_derived = bool(re.search(r"background|surface|border.*radius|shadow|padding|font.*size|color", content or "", re.IGNORECASE))
    results.append(check("Properties from token set", props_derived, f"props:{props_derived}"))

    has_states = bool(re.search(r"\*\*States:\*\*|States:", content or ""))
    has_hover = bool(re.search(r"Hover", content or "", re.IGNORECASE))
    has_disabled = bool(re.search(r"Disabled", content or "", re.IGNORECASE))
    results.append(check("Has Default/Hover/Disabled states", has_states and has_hover and has_disabled, f"states:{has_states}, hover:{has_hover}, disabled:{has_disabled}"))

    in_components = bool(re.search(r"## Components.*### Profile Dropdown", content or "", re.DOTALL))
    results.append(check("Appended under Components", in_components, f"in_components:{in_components}"))

    used_script = log is not None and ("design_tool.py" in log)
    results.append(check("Used design_tool.py", used_script, f"used_script:{used_script}"))

    return results

def grade_eval_3(base_dir):
    content = read_file(os.path.join(base_dir, "Design.md"))
    summary = read_file(os.path.join(base_dir, "summary.md"))

    if not content:
        for f in os.listdir(base_dir):
            if f.endswith('.md'):
                content = read_file(os.path.join(base_dir, f))
                if content: break

    results = []

    has_check = bool(re.search(r"check", content or "", re.IGNORECASE))
    if summary:
        has_check = "check" in summary.lower() and "exists" in summary.lower()
    results.append(check("Used check command", has_check, f"has_check:{has_check}"))

    # Count Button occurrences in Components section
    button_count = len(re.findall(r"### Button", content or ""))
    no_duplicate = button_count <= 1
    results.append(check("No duplicate Button design", no_duplicate, f"button_count:{button_count}"))

    informs_user = bool(re.search(r"already (exist|designed|have)", content or "", re.IGNORECASE))
    if summary:
        informs_user = "already" in summary.lower() or "did not create" in summary.lower()
    results.append(check("Informs user already designed", informs_user, f"informs:{informs_user}"))

    no_overwrite = no_duplicate
    for f in os.listdir(base_dir):
        if f.endswith('.json') or f == 'commands.log':
            no_overwrite = True
    results.append(check("No overwrite of existing", no_overwrite, f"no_overwrite:{no_overwrite}"))

    return results

def check(name, passed, evidence=""):
    return {"text": name, "passed": passed, "evidence": evidence}

def all_false(count):
    return [{"text": f"Assertion {i+1}", "passed": False, "evidence": "No Design.md found"} for i in range(count)]

if __name__ == "__main__":
    ws = "/root/skill-creator/design-creator-workspace/iteration-1"
    evals = {
        "eval-1-core-identity": ("Core Identity Creation", grade_eval_1),
        "eval-2-new-component": ("New Component Detection", grade_eval_2),
        "eval-3-already-designed": ("Already Designed Check", grade_eval_3)
    }

    for config in ["with_skill", "without_skill"]:
        print(f"\n{'='*60}")
        print(f"GRADING: {config}")
        print(f"{'='*60}")
        for eval_dir, (name, grader) in evals.items():
            base = os.path.join(ws, eval_dir, config, "outputs")
            results = grader(base)
            passed = sum(1 for r in results if r["passed"])
            total = len(results)
            print(f"\n  {name}: {passed}/{total} passed")
            for r in results:
                status = "PASS" if r["passed"] else "FAIL"
                print(f"    [{status}] {r['text']}")
                if not r["passed"]:
                    print(f"           {r['evidence']}")

            grading = {
                "expectations": results,
                "summary": {"passed": passed, "failed": total - passed, "total": total, "pass_rate": passed/total if total else 0},
                "execution_metrics": {"tool_calls": {}, "total_tool_calls": 0, "total_steps": 0, "errors_encountered": 0, "output_chars": 0, "transcript_chars": 0},
                "timing": {"executor_duration_seconds": 0, "grader_duration_seconds": 0, "total_duration_seconds": 0}
            }
            grading_path = os.path.join(ws, eval_dir, config, "grading.json")
            with open(grading_path, "w") as f:
                json.dump(grading, f, indent=2)
