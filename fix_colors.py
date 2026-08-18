import re

with open('E:/RobotCommandSimulator/frontend/robot_canvas.py', encoding='utf-8') as f:
    content = f.read()

# Replace alpha hex patterns in fill/outline strings
# Pattern: string + "XX" where XX is alpha (e.g., C["eye"] + "33")
replacements = [
    (r'C\["eye"\] \+ "33"',      '"#1b2d42"'),
    (r'C\["eye"\] \+ "44"',      '"#1e3555"'),
    (r'C\["body"\] \+ "33"',     '"#1a2f50"'),
    (r'C\["shield"\] \+ "22"',   '"#0d2e1a"'),
    (r'C\["antenna"\] \+ "33"',  '"#1f1a0d"'),
    (r'C\["trail"\]',            '"#388bfd"'),
    (r'#f8514915',               '#0d1117'),
    (r'#f8514960',               '#8a2b28'),
    (r'#f85149.*?(?=")',         '#f85149'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Also fix any leftover 8-char hex colors
content = re.sub(r'#([0-9a-fA-F]{6})[0-9a-fA-F]{2}', r'#\1', content)

with open('E:/RobotCommandSimulator/frontend/robot_canvas.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed robot_canvas.py colors")
