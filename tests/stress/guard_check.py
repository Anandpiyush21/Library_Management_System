"""Audit auth guards, CSRF verification and CSRF fields page by page."""
import re, glob

PUBLIC = {'index.php', 'signup.php', 'adminlogin.php', 'check_availability.php',
          'logout.php', 'admin/index.php', 'admin/logout.php'}
NON_PAGE = {'includes/config.php', 'includes/auth.php', 'includes/library.php',
            'includes/header.php', 'includes/footer.php',
            'admin/includes/config.php', 'admin/includes/notify.php',
            'admin/includes/header.php', 'admin/includes/footer.php'}

files = sorted(glob.glob('*.php') + glob.glob('admin/*.php') +
               glob.glob('includes/*.php') + glob.glob('admin/includes/*.php'))

rows, findings = [], []
for p in files:
    if p in NON_PAGE:
        continue
    src = open(p).read()
    guard = ('lms_require_admin' in src and 'admin') or ('lms_require_student' in src and 'student') or '-'
    # POST handlers: if (isset($_POST['x']))
    handlers = re.findall(r"isset\(\s*\$_POST\['(\w+)'\]\s*\)", src)
    verifies = src.count('lms_csrf_verify()')
    # forms that POST
    forms = re.findall(r'<form[^>]*method\s*=\s*["\']post["\'][^>]*>', src, re.I)
    fields = src.count('lms_csrf_field()')
    rows.append((p, guard, len(handlers), verifies, len(forms), fields))

    if p not in PUBLIC and guard == '-':
        findings.append(f"{p}: page has NO auth guard")
    if handlers and verifies == 0:
        findings.append(f"{p}: {len(handlers)} POST handler(s) {handlers} but no lms_csrf_verify()")
    if len(forms) > fields:
        findings.append(f"{p}: {len(forms)} POST form(s) but only {fields} CSRF field(s)")
    if re.search(r"\$_GET\['(del|inid|id)'\]", src):
        findings.append(f"{p}: still performs a state change from a GET parameter")

w = max(len(r[0]) for r in rows)
print(f"{'page'.ljust(w)}  guard    POSTh  verify  forms  fields")
print('-' * (w + 40))
for p, g, h, v, f, c in rows:
    print(f"{p.ljust(w)}  {g:7}  {h:5}  {v:6}  {f:5}  {c:6}")

print("\n" + "=" * 78)
if findings:
    print(f"{len(findings)} FINDING(S):")
    for f in findings:
        print("  -", f)
else:
    print("Every non-public page is guarded; every POST handler verifies CSRF; every POST form carries a token.")
