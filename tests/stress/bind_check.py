"""Check that every prepared statement binds exactly the placeholders it declares."""
import re, glob

files = sorted(glob.glob('*.php') + glob.glob('admin/*.php') +
               glob.glob('includes/*.php') + glob.glob('admin/includes/*.php'))
issues, checked = [], 0

for p in files:
    src = open(p).read()
    # variable -> SQL text (last assignment wins per file scan position)
    assigns = {}
    for m in re.finditer(r'\$(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')\s*;', src, re.S):
        assigns.setdefault(m.group(1), []).append((m.start(), m.group(2)[1:-1]))

    for m in re.finditer(r'->prepare\(\s*(\$(\w+)|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', src, re.S):
        pos = m.start()
        if m.group(2):                       # prepare($sql)
            cands = [t for off, t in assigns.get(m.group(2), []) if off < pos]
            if not cands:
                continue
            sql = cands[-1]
        else:
            sql = m.group(1)[1:-1]
        if not re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', sql, re.I):
            continue
        placeholders = set(re.findall(r':(\w+)', sql))
        if not placeholders:
            continue
        checked += 1
        window = src[pos:pos + 1400]
        bound = set(re.findall(r"bindParam\(\s*'?:(\w+)", window))
        bound |= set(re.findall(r"bindValue\(\s*'?:(\w+)", window))
        ex = re.search(r'->execute\(\s*\[(.*?)\]\s*\)', window, re.S)
        if ex:
            bound |= set(re.findall(r"':?(\w+)'\s*=>", ex.group(1)))
        line = src[:pos].count('\n') + 1
        missing, extra = placeholders - bound, bound - placeholders
        if missing:
            issues.append((p, line, f"placeholder(s) never bound: {sorted(missing)}", sql))
        if extra:
            issues.append((p, line, f"bound but not in SQL: {sorted(extra)}", sql))

print(f"Checked {checked} parameterised statements")
print("=" * 78)
if issues:
    for p, line, why, sql in issues:
        print(f"  {p}:{line}  {why}")
        print(f"      {' '.join(sql.split())[:130]}")
else:
    print("Every declared placeholder is bound, and nothing extra is bound.")
