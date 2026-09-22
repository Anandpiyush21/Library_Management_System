"""Cross-check every SQL statement in the PHP against database/library.sql."""
import re, glob, sys, collections

sql = open('database/library.sql').read()

# --- parse CREATE TABLE blocks -------------------------------------------
tables = {}
for m in re.finditer(r'CREATE TABLE `(\w+)` \((.*?)\n\) ENGINE', sql, re.S):
    name, body = m.group(1), m.group(2)
    cols = []
    for line in body.split('\n'):
        line = line.strip()
        cm = re.match(r'`(\w+)`\s+\w', line)
        if cm and not line.upper().startswith(('PRIMARY', 'UNIQUE', 'KEY', 'CONSTRAINT')):
            cols.append(cm.group(1))
    tables[name] = cols

print("Schema parsed:")
for t, c in tables.items():
    print(f"  {t:24} {len(c)} columns")

lower = {t.lower(): {c.lower() for c in cols} for t, cols in tables.items()}
allcols = set().union(*lower.values())

# --- extract SQL strings from PHP ----------------------------------------
KW = re.compile(r'\b(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b', re.I)
files = sorted(glob.glob('*.php') + glob.glob('admin/*.php') +
               glob.glob('includes/*.php') + glob.glob('admin/includes/*.php'))

stmts = []
for p in files:
    src = open(p).read()
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'', src, re.S):
        q = m.group(1) if m.group(1) is not None else m.group(2)
        if not q or not KW.search(q):
            continue
        # skip strings that are actually PHP source picked up across a quote
        # boundary: real SQL has no '=>', '$var', '->' or statement semicolons
        if re.search(r'=>|\$\w|->|;\s*\w', q):
            continue
        if ('FROM' in q.upper() or 'INTO' in q.upper() or
                re.search(r'\bUPDATE\s+\w+\s+SET\b', q, re.I)):
            line = src[:m.start()].count('\n') + 1
            stmts.append((p, line, ' '.join(q.split())))

print(f"\n{len(stmts)} SQL statements found in {len(files)} PHP files\n")

problems = []

for p, line, q in stmts:
    # tables referenced
    refs = set()
    for m in re.finditer(r'\b(?:FROM|JOIN|INTO|UPDATE)\s+`?(\w+)`?', q, re.I):
        refs.add(m.group(1).lower())
    refs.discard('set')
    for t in refs:
        if t not in lower:
            problems.append((p, line, f"unknown table `{t}`", q))

    # alias map: "tblbooks b" / "tblbooks AS b"
    alias = {}
    for m in re.finditer(r'\b(?:FROM|JOIN|INTO|UPDATE)\s+`?(\w+)`?\s+(?:AS\s+)?(?!WHERE|SET|ON|VALUES|ORDER|GROUP|LEFT|JOIN|INNER|WHERE)([a-z]\w*)\b', q, re.I):
        t, a = m.group(1).lower(), m.group(2).lower()
        if t in lower and a not in ('set', 'values', 'where', 'on', 'order', 'group', 'left', 'join', 'inner', 'select'):
            alias[a] = t

    # qualified column references  alias.Col / table.Col
    for m in re.finditer(r'\b(\w+)\.(\w+)\b', q):
        qual, col = m.group(1).lower(), m.group(2).lower()
        tbl = alias.get(qual, qual if qual in lower else None)
        if tbl is None:
            continue
        if col not in lower[tbl]:
            problems.append((p, line, f"`{tbl}` has no column `{col}`", q))

    # unqualified columns when exactly one table is involved
    if len(refs) == 1 and not alias:
        tbl = next(iter(refs))
        body = re.sub(r"'[^']*'", "''", q)
        for m in re.finditer(r'(?<![.\w:$])\b([A-Za-z_]\w*)\b', body):
            w = m.group(1)
            if w.upper() in {
                'SELECT','FROM','WHERE','AND','OR','INSERT','INTO','VALUES','UPDATE','SET','DELETE',
                'ORDER','BY','GROUP','LIMIT','DESC','ASC','JOIN','LEFT','INNER','ON','AS','COUNT',
                'SUM','COALESCE','DISTINCT','NOW','DATE_SUB','INTERVAL','DAY','LIKE','NOT','NULL',
                'IS','MIN','MAX','FOR','UPDATE','CASE','WHEN','THEN','ELSE','END','IN'}:
                continue
            if w.lower() == tbl:
                continue
            if w.lower() in lower[tbl]:
                continue
            if w.lower() in allcols:
                problems.append((p, line, f"column `{w}` not in `{tbl}` (exists elsewhere)", q))

print("=" * 78)
if problems:
    print(f"{len(problems)} SCHEMA MISMATCH(ES):\n")
    for p, line, why, q in problems:
        print(f"  {p}:{line}  {why}")
        print(f"      {q[:150]}")
else:
    print("No schema mismatches: every table and column referenced by the PHP exists.")
