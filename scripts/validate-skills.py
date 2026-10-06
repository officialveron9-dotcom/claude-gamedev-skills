"""Check every SKILL.md under plugins/: frontmatter keys, name = folder, description length,
file length and relative Markdown links. Run: python3 scripts/validate-skills.py"""
import os
import re
import sys

# Keys that claude.ai uploads and the Agent Skills spec accept; anything else breaks a ZIP upload.
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_DESCRIPTION = 1024
MAX_LINES = 500

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
failures = 0


def markdown_links(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # ignore code blocks
    text = re.sub(r"`[^`\n]*`", "", text)               # ignore inline code
    for target in re.findall(r"\]\(([^)\s#]+)(?:#[^)]*)?\)", text):
        if not re.match(r"^[a-z][a-z0-9+.-]*:", target):  # skip http:, mailto: ...
            yield target


for dirpath, _, files in sorted(os.walk(os.path.join(root, "plugins"))):
    if "SKILL.md" not in files:
        continue
    skill = os.path.basename(dirpath)
    text = open(os.path.join(dirpath, "SKILL.md"), encoding="utf-8").read()
    issues = []
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        issues.append("missing frontmatter")
    else:
        frontmatter = match.group(1)
        keys = set(re.findall(r"^([A-Za-z_-]+):", frontmatter, re.M))
        if keys - ALLOWED_KEYS:
            issues.append(f"unsupported keys {sorted(keys - ALLOWED_KEYS)}")
        name = re.search(r"^name:\s*\"?([^\"\n]+)\"?\s*$", frontmatter, re.M)
        if not name or name.group(1).strip() != skill:
            issues.append("name does not match folder")
        desc = re.search(r"^description:\s*(.+?)(?=^[A-Za-z_-]+:|\Z)", frontmatter, re.M | re.S)
        length = len(desc.group(1).strip().strip('"')) if desc else 0
        if not length:
            issues.append("missing description")
        elif length > MAX_DESCRIPTION:
            issues.append(f"description has {length} chars (max {MAX_DESCRIPTION})")
    if text.count("\n") > MAX_LINES:
        issues.append(f"SKILL.md has more than {MAX_LINES} lines")
    for sub, _, names in os.walk(dirpath):
        for md in (n for n in names if n.endswith(".md")):
            path = os.path.join(sub, md)
            for target in markdown_links(open(path, encoding="utf-8").read()):
                if not os.path.exists(os.path.normpath(os.path.join(sub, target))):
                    issues.append(f"broken link in {os.path.relpath(path, dirpath)}: {target}")
    if issues:
        failures += 1
        print(f"{os.path.relpath(dirpath, root)}:\n  " + "\n  ".join(issues))

print(f"{failures} skill(s) with problems" if failures else "All skills OK")
sys.exit(1 if failures else 0)
