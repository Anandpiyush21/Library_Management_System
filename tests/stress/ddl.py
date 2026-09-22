"""Translate the MySQL DDL in database/library.sql into SQLite DDL.

The point is to keep the *constraints* (PK, UNIQUE, FK, NOT NULL, defaults)
intact so the stress run exercises the real schema design, not a simplified one.
"""
import re

def translate(path='database/library.sql'):
    sql = open(path).read()
    out = []
    for m in re.finditer(r'CREATE TABLE `(\w+)` \((.*?)\n\) ENGINE[^;]*;', sql, re.S):
        name, body = m.group(1), m.group(2)
        lines, constraints = [], []
        for raw in body.split('\n'):
            l = raw.strip().rstrip(',')
            if not l:
                continue
            l = re.sub(r"COMMENT\s+'(?:[^']|'')*'", '', l).strip()
            l = re.sub(r'\bON UPDATE CURRENT_TIMESTAMP\b', '', l, flags=re.I).strip()
            up = l.upper()
            if up.startswith('KEY '):
                continue                                  # plain indexes: not needed
            if up.startswith('PRIMARY KEY') or up.startswith('UNIQUE KEY') or up.startswith('CONSTRAINT'):
                c = re.sub(r'UNIQUE KEY `\w+`', 'UNIQUE', l, flags=re.I)
                c = re.sub(r'CONSTRAINT `\w+` ', '', c, flags=re.I)
                constraints.append(c)
                continue
            cm = re.match(r'`(\w+)`\s+(.*)$', l)
            if not cm:
                continue
            col, rest = cm.group(1), cm.group(2)
            typ = rest.split()[0].upper()
            if 'AUTO_INCREMENT' in rest.upper():
                lines.append(f'`{col}` INTEGER PRIMARY KEY AUTOINCREMENT')
                continue
            if typ.startswith('INT') or typ.startswith('TINYINT'):
                t = 'INTEGER'
            elif typ.startswith('DECIMAL'):
                t = 'REAL'
            elif typ.startswith('TIMESTAMP') or typ.startswith('DATETIME'):
                t = 'TEXT'
            elif typ.startswith('TEXT'):
                t = 'TEXT'
            else:
                t = re.sub(r'VARCHAR', 'TEXT', typ)
            extra = ''
            if re.search(r'\bNOT NULL\b', rest, re.I):
                extra += ' NOT NULL'
            dm = re.search(r'DEFAULT\s+(CURRENT_TIMESTAMP|NULL|[\d.]+|\'[^\']*\')', rest, re.I)
            if dm:
                d = dm.group(1)
                extra += " DEFAULT (datetime('now'))" if d.upper() == 'CURRENT_TIMESTAMP' else f' DEFAULT {d}'
            lines.append(f'`{col}` {t}{extra}')
        # a table whose PK was AUTO_INCREMENT already declares it inline
        constraints = [c for c in constraints if not c.upper().startswith('PRIMARY KEY')
                       or not any('AUTOINCREMENT' in l for l in lines)]
        out.append(f"CREATE TABLE `{name}` (\n  " + ",\n  ".join(lines + constraints) + "\n);")
    return out

if __name__ == '__main__':
    for stmt in translate():
        print(stmt)
