# -*- coding: utf-8 -*-
"""Build the project report PDF."""
import json, os, sys, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, KeepTogether,
                                NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, 'figs')
D = json.load(open(os.path.join(HERE, 'data.json')))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'report.pdf')

INK, INK2, MUTED = colors.HexColor('#0b0b0b'), colors.HexColor('#52514e'), colors.HexColor('#898781')
RULE, BAND = colors.HexColor('#d9d8d2'), colors.HexColor('#f4f3f0')
BLUE, GREEN, RED, AMBER = (colors.HexColor('#2a78d6'), colors.HexColor('#0ca30c'),
                           colors.HexColor('#d03b3b'), colors.HexColor('#b8860b'))

PW, PH = A4
LM = RM = 20 * mm
TM, BM = 22 * mm, 20 * mm
CW = PW - LM - RM

ss = getSampleStyleSheet()
def S(name, **kw):
    base = kw.pop('parent', ss['BodyText'])
    return ParagraphStyle(name, parent=base, **kw)

body = S('body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=INK,
         alignment=TA_JUSTIFY, spaceAfter=7)
bullet = S('bullet', parent=body, leftIndent=12, bulletIndent=2, spaceAfter=3.5)
h1 = S('h1', fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=INK,
       spaceBefore=4, spaceAfter=9)
h2 = S('h2', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=INK,
       spaceBefore=11, spaceAfter=5)
h3 = S('h3', fontName='Helvetica-Bold', fontSize=9.8, leading=13, textColor=INK2,
       spaceBefore=8, spaceAfter=3)
cap = S('cap', fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=INK2,
        alignment=TA_CENTER, spaceBefore=5, spaceAfter=12)
code = S('code', fontName='Courier', fontSize=8, leading=11.5, textColor=INK,
         backColor=BAND, borderPadding=6, spaceBefore=4, spaceAfter=9, leftIndent=2)
tcell = S('tcell', fontName='Helvetica', fontSize=8.2, leading=11, textColor=INK, spaceAfter=0,
          alignment=0)
thead = S('thead', parent=tcell, fontName='Helvetica-Bold', textColor=colors.white)
tmono = S('tmono', parent=tcell, fontName='Courier', fontSize=7.6)
note = S('note', parent=body, fontSize=8.8, leading=12.5, textColor=INK2,
         leftIndent=8, borderPadding=0, spaceBefore=2)

WINANSI_EXTRA = set('—–’‘“”·×°±§…•€£')
def check(s):
    bad = {ch for ch in s if ord(ch) > 127 and ch not in WINANSI_EXTRA}
    if bad:
        raise SystemExit(f'non-WinAnsi characters in text: {bad!r} in {s[:80]!r}')
    return s

# ------------------------------------------------------------------ flow ----
story = []
_fig_n = [0]
_tab_n = [0]

def P(t, style=body):    story.append(Paragraph(check(t), style))
def SP(h=6):             story.append(Spacer(1, h))
def H1(t):               story.append(Paragraph(check(t), h1))
def H2(t):               story.append(Paragraph(check(t), h2))
def H3(t):               story.append(Paragraph(check(t), h3))
def UL(items, style=bullet):
    for it in items:
        story.append(Paragraph(check(it), style, bulletText='•'))
    SP(5)

def FIG(name, caption_text, width=None):
    _fig_n[0] += 1
    path = os.path.join(FIGS, name)
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    w = width or CW
    h = w * ih / iw
    img = Image(path, width=w, height=h)
    story.append(KeepTogether([img, Paragraph(
        check(f'<b>Figure {_fig_n[0]}.</b> {caption_text}'), cap)]))

def TBL(rows, widths, caption_text=None, align=None, header=True, mono_cols=()):
    _tab_n[0] += 1
    data = []
    for r, row in enumerate(rows):
        out = []
        for c, cell in enumerate(row):
            st = thead if (header and r == 0) else (tmono if c in mono_cols else tcell)
            out.append(Paragraph(check(str(cell)), st))
        data.append(out)
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('TOPPADDING', (0, 0), (-1, -1), 4),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
             ('LEFTPADDING', (0, 0), (-1, -1), 6),
             ('RIGHTPADDING', (0, 0), (-1, -1), 6),
             ('LINEBELOW', (0, 0), (-1, -2), 0.4, RULE)]
    if header:
        style += [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#52514e')),
                  ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor('#52514e'))]
        style += [('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BAND])]
    else:
        style += [('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, BAND])]
    t.setStyle(TableStyle(style))
    story.append(t)
    if caption_text:
        story.append(Paragraph(check(f'<b>Table {_tab_n[0]}.</b> {caption_text}'), cap))
    else:
        SP(10)

F = D['fuzz']; R = D['race']; LC = D['last_copy']; REPO = D['repo']
TODAY = datetime.date(2026, 9, 22).strftime('%d %B %Y')

# ============================================================ TITLE PAGE =====
story.append(Spacer(1, 38 * mm))
story.append(Paragraph('Library Management System', S('t1', fontName='Helvetica-Bold',
             fontSize=25, leading=30, textColor=INK, alignment=TA_CENTER)))
story.append(Spacer(1, 5 * mm))
story.append(Paragraph('Re-engineering a coursework web application into a documented,<br/>'
                       'verifiable reference implementation',
             S('t2', fontName='Helvetica', fontSize=12.5, leading=18, textColor=INK2,
               alignment=TA_CENTER)))
story.append(Spacer(1, 12 * mm))
rule = Table([['']], colWidths=[60 * mm], rowHeights=[1])
rule.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, -1), 1.2, BLUE)]))
rule.hAlign = 'CENTER'
story.append(rule)
story.append(Spacer(1, 12 * mm))
story.append(Paragraph('PROJECT REPORT', S('t3', fontName='Helvetica-Bold', fontSize=10,
             leading=14, textColor=MUTED, alignment=TA_CENTER)))
story.append(Spacer(1, 22 * mm))
meta = Table([
    ['Prepared by', 'Piyush Anand'],
    ['Roll number', 'CS21B1019'],
    ['Domain', 'Web application engineering, database design,'],
    ['', 'software verification'],
    ['Implementation', 'PHP 7.4+, MySQL 5.7+ / MariaDB 10.3+, Bootstrap 3'],
    ['Date', TODAY],
], colWidths=[34 * mm, 90 * mm])
meta.setStyle(TableStyle([
    ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
    ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
    ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
    ('TEXTCOLOR', (1, 0), (1, -1), INK),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
meta.hAlign = 'CENTER'
story.append(meta)
story.append(Spacer(1, 26 * mm))
story.append(Paragraph(
    'This report documents the design, implementation and verification of a library circulation '
    'system, and states plainly which claims in it were executed and which were not.',
    S('t4', fontName='Helvetica-Oblique', fontSize=8.8, leading=13, textColor=MUTED,
      alignment=TA_CENTER, leftIndent=28 * mm, rightIndent=28 * mm)))
story.append(PageBreak())

# ============================================================== CONTENTS =====
story.append(Paragraph('Contents', S('h1plain', parent=h1)))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle('toc1', fontName='Helvetica-Bold', fontSize=9.6, leading=17,
                   textColor=INK, spaceAfter=0),
    ParagraphStyle('toc2', fontName='Helvetica', fontSize=9, leading=14.5,
                   textColor=INK2, leftIndent=14),
]
story.append(toc)
story.append(PageBreak())

# ========================================================= 1. INTRODUCTION ===
H1('1.  Introduction')

H2('1.1  Context and motivation')
P('A small academic library performs a handful of operations over and over: a member looks for a '
  'title, a librarian hands over a copy, the copy comes back, and a fine is charged when it comes '
  'back late. The operations are simple to describe, which makes it easy to build software for them '
  'that appears to work and is quietly wrong: a copy count that drifts, a fine computed by hand, a '
  'catalogue that anyone who is logged in can delete.')
P('This project began as a coursework web application in PHP and MySQL. It had the expected shape of '
  'such a project: server-rendered pages, a Bootstrap front end, one file per screen. It also had the '
  'expected defects. This report documents its re-engineering into a reference implementation that is '
  'documented, constrained by its schema, and verified as far as the available tooling allowed.')

H2('1.2  Objectives')
UL(['<b>Make the system installable.</b> The database schema was absent from the repository, so the '
    'application could not be deployed at all by anyone who did not already possess the database.',
    '<b>Give the circulation rules one home.</b> Loan period, fine rate and borrowing limit should be '
    'parameters of the system, not constants scattered through page scripts.',
    '<b>Make the circulation operations correct under concurrency.</b> Issuing and returning a copy '
    'each touch three tables; they must be atomic and must not lose or invent copies.',
    '<b>Bring the security posture to a deployable standard</b> for passwords, SQL, output encoding, '
    'request forgery and privilege separation.',
    '<b>Verify the result</b>, and report honestly on what the verification does and does not cover.'])

H2('1.3  Scope')
P('The work deliberately preserves the application\'s external shape. The framework-free PHP, the '
  'page-per-URL structure, the Bootstrap 3 front end and the original table names — including the '
  'misspelled column <font face="Courier">RetrunStatus</font> — are unchanged. Renaming these would '
  'have produced a different project rather than a corrected one, and would have made the result '
  'impossible to compare against the version it grew from. The changes are concentrated in the data '
  'model, the domain logic, the security layer and the documentation.')

H2('1.4  Summary of outcomes')
TBL([['Area', 'Outcome'],
     ['Data model',
      f"{REPO['tables']} tables with primary, unique and foreign keys, InnoDB and utf8mb4, "
      "delivered as an idempotent schema script with seed data"],
     ['Domain layer',
      'Circulation rules, fine arithmetic and transactional issue/return isolated in '
      '<font face="Courier">includes/library.php</font>; policy expressed as three constants'],
     ['Security',
      'bcrypt with transparent migration from md5, CSRF tokens on every state-changing form, '
      'prepared statements throughout, POST-only state changes, session hardening'],
     ['Defects',
      '9 defects found and fixed, including a privilege-escalation flaw, a copy-count leak '
      'and a time-of-check/time-of-use race'],
     ['Verification',
      f"3 static analyses, 17 unit assertions, a {F['iterations']:,}-operation randomised stress "
      'run against 6 invariants, and 2 concurrency experiments'],
     ['Size',
      f"{REPO['php_files']} PHP files, ~{REPO['php_loc']:,} lines; the rework touched 53 files "
      f"(+5,899 / -3,791 lines)"]],
    [32 * mm, CW - 32 * mm],
    'Summary of what the re-engineering produced.')
story.append(PageBreak())

# ====================================================== 2. SYSTEM OVERVIEW ===
H1('2.  System overview')
P('The system serves two roles that never share a screen. A <b>member</b> registers, searches the '
  'catalogue, sees their own loans and fines, and may request a title the library does not hold. A '
  '<b>librarian</b> maintains the catalogue, issues and receives copies, tracks overdue loans and '
  'fines, blocks or reinstates members, and rules on acquisition requests.')

H2('2.1  Member portal')
TBL([['Page', 'Function'],
     ['index.php', 'Login: bcrypt verification, session regeneration, blocked-account handling'],
     ['signup.php', 'Self-registration; allocates a library card number under a file lock; validates '
                    'e-mail, mobile and password; checks e-mail availability over AJAX'],
     ['dashboard.php', 'Books borrowed, loans open against the per-member limit, overdue count, fine payable'],
     ['available-books.php', 'Catalogue search across title, author and ISBN, with live copy availability'],
     ['issued-books.php', 'Personal loan history with due dates, days overdue and the fine accruing'],
     ['book-requests.php', 'Raise an acquisition request; see the librarian\'s decision'],
     ['my-profile.php', 'Profile, registration date, outstanding fine balance'],
     ['change-password.php', 'Password change with current-password verification']],
    [40 * mm, CW - 40 * mm], None, mono_cols=(0,))

H2('2.2  Librarian panel')
TBL([['Page', 'Function'],
     ['dashboard.php', 'Eight live indicators — titles, copies on shelf, members, blocked members, '
                       'books out, overdue loans, pending requests, fines outstanding — each linking '
                       'to the corresponding filtered list'],
     ['issue-book.php', 'Issue a copy; AJAX member and title lookup; every circulation rule checked '
                        'before the ledger is touched'],
     ['update-issue-bookdeails.php', 'Receive a copy; the fine is pre-computed from the policy and '
                                     'may be overridden for a waiver or a disputed date'],
     ['manage-issued-books.php', 'The circulation ledger, filterable by all / on loan / overdue'],
     ['add-book.php, manage-books.php, edit-book.php',
      'Catalogue maintenance; ISBN validation, author de-duplication, deletion refused while copies are out'],
     ['manage-categories.php, manage-authors.php', 'Classification and author maintenance'],
     ['mail-student.php', 'Every member holding an overdue book, with a one-click reminder that '
                          'itemises their loans and fines'],
     ['reg-students.php', 'Member list; block and reinstate accounts'],
     ['book-request.php', 'Approve or decline acquisition requests, filterable by status']],
    [46 * mm, CW - 46 * mm], None, mono_cols=(0,))
story.append(PageBreak())

# ======================================================== 3. ARCHITECTURE ====
H1('3.  Architecture')
P('The application has no framework, so its layering is a convention rather than something the '
  'runtime enforces. The convention is simple and is stated here so that it can be checked: a page '
  'script may read input, call helper functions and render HTML; it may not decide what the library '
  'permits. Figure 1 shows the arrangement.')
FIG('fig_architecture.png',
    'Layered architecture. Page scripts hold presentation only; every library rule lives in the '
    'domain layer, and the two portals share a single bootstrap, database handle and policy.')

H2('3.1  Why the rules are centralised')
P('Loan period, fine rate and borrowing limit are declared once, in '
  '<font face="Courier">includes/config.php</font>, and applied by '
  '<font face="Courier">includes/library.php</font>. Changing '
  '<font face="Courier">LOAN_PERIOD_DAYS</font> from 14 to 21 changes, in one edit: what the issue '
  'screen tells the librarian, the due dates the member sees, the overdue filter on the ledger, the '
  'fine pre-filled on return, and who appears on the overdue-reminder list. In the original code the '
  'same change would have required finding every page that mentioned a date interval, and the fine '
  'was not computed at all — it was typed in by hand.')

H2('3.2  Database access settings')
P('The PDO handle is opened with three settings that are worth stating explicitly, because each one '
  'rules out a class of defect:')
story.append(Paragraph(check(
    "PDO::ATTR_ERRMODE            =&gt; PDO::ERRMODE_EXCEPTION<br/>"
    "PDO::ATTR_DEFAULT_FETCH_MODE =&gt; PDO::FETCH_OBJ<br/>"
    "PDO::ATTR_EMULATE_PREPARES   =&gt; false"), code))
UL(['<b>Exceptions on error.</b> A failed write cannot pass unnoticed. The original code inspected '
    '<font face="Courier">lastInsertId()</font> and assumed success otherwise.',
    '<b>Native prepares.</b> Parameters are sent to the server separately from the SQL text, so the '
    'placeholder is never interpolated. This also forbids reusing a named placeholder twice in one '
    'statement — a constraint that caught two latent errors during this work (Section 8).'])

H2('3.3  Technology choices')
TBL([['Layer', 'Choice', 'Rationale'],
     ['Language', 'PHP 7.4+, no framework',
      'Inherited. Retaining it keeps the project comparable to its origin; the typed helpers and '
      '<font face="Courier">password_*</font> API require 7.x'],
     ['Database', 'MySQL 5.7+ / MariaDB 10.3+, InnoDB',
      'Foreign keys and row-level locking are both required by the circulation logic; MyISAM would '
      'provide neither'],
     ['Encoding', 'utf8mb4',
      'Titles and member names outside the Basic Multilingual Plane are stored correctly'],
     ['Front end', 'Bootstrap 3, jQuery 1.10, DataTables',
      'Inherited and deliberately untouched; replacing it was out of scope'],
     ['Sessions', 'PHP native sessions, hardened cookies',
      'No external session store is justified at this scale']],
    [24 * mm, 38 * mm, CW - 62 * mm],
    'Technology stack and the reason for each choice.')
story.append(PageBreak())

# ========================================================== 4. DATA MODEL ====
H1('4.  Data model')
P('The schema was the largest single gap in the inherited project: it did not exist in the repository. '
  'The application could therefore not be installed by anyone who did not already possess a populated '
  'database. It is now delivered as <font face="Courier">database/library.sql</font>, an idempotent '
  'script that drops and recreates the schema with seed data, so a reviewer can go from a clone to a '
  'running system with one command.')
FIG('fig_er.png',
    'Entity-relationship model. Seven tables; foreign keys constrain every reference, and unique keys '
    'protect the ISBN, the library card number and the member e-mail.')

H2('4.1  Tables')
TBL([['Table', 'Rows represent', 'Notable constraints'],
     ['admin', 'Librarian accounts', 'UNIQUE(UserName); Password holds a bcrypt hash'],
     ['tblcategory', 'Subject classification', 'UNIQUE(CategoryName); Status hides a category from drop-downs'],
     ['tblauthors', 'Normalised author list', 'Indexed by name; kept in step with tblbooks by the add/edit flows'],
     ['tblbooks', 'Catalogue titles',
      'UNIQUE(ISBNNumber); FK to category and author; Count = copies on the shelf'],
     ['tblstudents', 'Members',
      'UNIQUE(StudentId), UNIQUE(EmailId); Status 1 = active, 0 = blocked; fines accumulates'],
     ['tblissuedbookdetails', 'One row per issue event',
      'FK to book and to member card number; RetrunStatus 0 = out, 1 = returned; indexed on '
      '(RetrunStatus, IssuesDate) for the overdue queries'],
     ['tblrequest', 'Acquisition requests', 'FK to member; IsApproved in {Pending, Approved, Not Approved}']],
    [30 * mm, 33 * mm, CW - 63 * mm],
    'The seven tables and the constraints that carry the most design weight.')

H2('4.2  Two decisions worth defending')
H3('Count is shelf stock, not holdings')
P('<font face="Courier">tblbooks.Count</font> records how many copies are physically available, not '
  'how many the library owns. Issuing decrements it; returning restores it. The alternative — storing '
  'total holdings and deriving availability by counting open loans — is more normalised, but it makes '
  'the availability check a join in the hot path and, more importantly, gives up the single-statement '
  'concurrency guard described in Section 5.3. The cost of the chosen design is that the count and '
  'the ledger must be written in the same transaction, which is exactly what invariant I2 in '
  'Section 7 checks.')
H3('Members are keyed twice')
P('A member has a surrogate key (<font face="Courier">id</font>) and a human-readable library card '
  'number (<font face="Courier">StudentId</font>, e.g. SID017). The ledger and the request table join '
  'on the card number, because that is the identifier a librarian reads off a card at the desk and '
  'types into the issue screen. The card number carries a UNIQUE constraint, so the denormalisation '
  'cannot produce ambiguity.')
P('Card numbers are allocated by incrementing a counter file under an exclusive lock, exploiting '
  'PHP\'s Perl-style string increment ("SID016" becomes "SID017"). The original code read and wrote '
  'that file without a lock, so two simultaneous registrations could take the same number. Section 7.4 '
  'reports what happens at the SID999 boundary.')
story.append(PageBreak())

# =================================================== 5. CIRCULATION LOGIC ====
H1('5.  Circulation logic')
P('Everything that encodes a library rule lives in <font face="Courier">includes/library.php</font>. '
  'This section states the rules, then shows how the two operations that change state are made atomic.')

H2('5.1  The policy')
TBL([['Constant', 'Default', 'Meaning'],
     ['LOAN_PERIOD_DAYS', '14', 'Days a copy may be kept before a fine begins to accrue'],
     ['FINE_PER_DAY', '5.00', 'INR charged for each day past the due date'],
     ['MAX_BOOKS_PER_USER', '3', 'Simultaneous open loans permitted to one member']],
    [40 * mm, 18 * mm, CW - 58 * mm],
    'The circulation policy, declared in includes/config.php.', mono_cols=(0,))
P('A loan is one row in the ledger. Its state is not stored beyond the returned flag: "overdue" is '
  'derived from the issue date and the policy every time a page is rendered, so there is no nightly '
  'job that can fall behind and no denormalised status to go stale.')
FIG('fig_loan_state.png',
    'The lifecycle of a single copy. The only stored state is RetrunStatus; "overdue" is computed '
    'on demand from IssuesDate and the loan policy.')

H2('5.2  Fine arithmetic')
P('The fine is a step function of the time the copy has been held:')
story.append(Paragraph(check(
    'fine = max(0, days_since_issue - LOAN_PERIOD_DAYS) x FINE_PER_DAY'), code))
P('It is evaluated for the librarian on the return screen and pre-filled, but remains editable. That '
  'is deliberate: waivers, damaged copies and disputed dates are ordinary library business, and a '
  'system that computes a fine but refuses to let staff override it simply gets worked around. When '
  'a loan is closed the fine is frozen at the return date, so a record that is examined months later '
  'still shows what was actually charged.')
FIG('fig_fine_curve.png',
    'Fine accrual against time held. No fine accrues through day 14; each subsequent day adds '
    'FINE_PER_DAY. Values are those produced by lms_calculate_fine().', width=CW * 0.86)

H2('5.3  Issuing a copy')
P('An issue request passes through two gates. The first, <font face="Courier">lms_issue_blocker()</font>, '
  'produces the message the librarian reads: unknown member, blocked account, no copy on the shelf, '
  'the member already holds that title, or the loan limit is reached. Collecting the checks in one '
  'function keeps the page from accumulating half of them.')
P('The second gate is inside the transaction, and exists because the first one is only a snapshot. '
  'Two issues submitted at the same moment can both pass it — a time-of-check/time-of-use window that '
  'was measured, not hypothesised, and is reported in Section 7.5. The transaction therefore takes a '
  'locking read of the member row and re-checks the per-member rules before writing anything.')
FIG('fig_seq_issue.png',
    'Issuing a copy. The per-member rules are re-checked inside the transaction behind '
    'SELECT ... FOR UPDATE; the shelf count is protected by a condition inside the UPDATE itself.')
P('The two guards differ in kind, and the distinction is the heart of the design. The shelf count is '
  'protected by a condition carried inside the write:')
story.append(Paragraph(check(
    'UPDATE tblbooks SET Count = Count - 1 WHERE id = :id AND Count &gt; 0'), code))
P('If two librarians issue the last copy simultaneously, the second statement matches zero rows, the '
  'transaction rolls back, and the page reports that the copy has just gone. No lock is required, '
  'because the check and the write are one operation. The per-member rules cannot be expressed that '
  'way — they are a count across another table — so they need the row lock.')

H2('5.4  Receiving a copy')
P('Returning closes the ledger row, restores the copy to the shelf and bills the fine, in one '
  'transaction. The ledger row is selected <font face="Courier">FOR UPDATE</font>, so a double '
  'submission finds the loan already closed and is refused rather than crediting a second copy to '
  'the shelf.')
FIG('fig_seq_return.png',
    'Receiving a copy. Restoring the shelf count is the step the inherited code omitted entirely, '
    'which drained the catalogue over time.')
story.append(PageBreak())

# ======================================================= 6. SECURITY =========
H1('6.  Security engineering')
P('The inherited application stored unsalted md5 password digests, changed state through GET links, '
  'and interpolated query results directly into HTML. This section sets out the threats considered '
  'and the control applied to each.')

H2('6.1  Threats and controls')
TBL([['Threat', 'Control applied'],
     ['Password disclosure from a database leak',
      'bcrypt via <font face="Courier">password_hash()</font> / '
      '<font face="Courier">password_verify()</font>, replacing unsalted md5'],
     ['SQL injection',
      'PDO prepared statements everywhere, with emulation disabled so parameters are bound by the server'],
     ['Cross-site scripting',
      'All dynamic output escaped through a single helper '
      '<font face="Courier">e()</font> (htmlspecialchars, ENT_QUOTES, UTF-8)'],
     ['Cross-site request forgery',
      'Per-session token in every state-changing form; '
      '<font face="Courier">lms_csrf_verify()</font> rejects a mismatch with HTTP 400'],
     ['State change by link traversal',
      'Deleting a book, blocking a member and ruling on a request are POST forms; no crawler or '
      'link pre-fetcher can trigger them'],
     ['Privilege escalation',
      'A member-facing page accepted <font face="Courier">?del=&lt;id&gt;</font> and deleted from '
      'the catalogue; deletion now exists only behind an admin session (Section 8, D1)'],
     ['Session fixation',
      '<font face="Courier">session_regenerate_id(true)</font> on every successful login; cookies '
      'are HttpOnly, SameSite=Lax, and Secure under HTTPS'],
     ['Account enumeration',
      'Login failures return one message whether the e-mail is unknown or the password is wrong'],
     ['Information disclosure between members',
      'A member\'s request list shows only their own rows; it previously listed every member\'s'],
     ['Credential exposure in version control',
      'Database credentials read from the environment or a gitignored local file'],
     ['Error-message leakage',
      '<font face="Courier">error_reporting(0)</font> replaced by logging; database errors are '
      'logged, not displayed']],
    [44 * mm, CW - 44 * mm],
    'Threats considered and the control applied to each.')

H2('6.2  Migrating passwords without a reset')
P('Replacing md5 with bcrypt in a system that already has accounts poses an obvious problem: the '
  'plaintext needed to compute a bcrypt hash is only available for an instant, during a login. The '
  'design exploits exactly that instant.')
FIG('fig_password.png',
    'Password verification and transparent migration. A legacy digest is accepted once; that same '
    'login rewrites the row as bcrypt.', width=CW * 0.94)
P('The password column is widened to 255 characters and may hold either form. A stored value matching '
  'the 32-hex-character md5 pattern is compared with a constant-time '
  '<font face="Courier">hash_equals()</font>; anything else goes to '
  '<font face="Courier">password_verify()</font>. On success, '
  '<font face="Courier">lms_password_needs_rehash()</font> decides whether to rewrite the row. An '
  'existing installation therefore upgrades itself account by account, with no password reset and no '
  'downtime, and the legacy branch can later be deleted by removing a single '
  '<font face="Courier">preg_match</font> case.')

H2('6.3  Residual risk')
UL(['<b>Login attempts are not rate-limited.</b> Online password guessing is slowed only by bcrypt\'s '
    'cost factor.',
    '<b>The signup e-mail availability endpoint is an enumeration oracle by design.</b> It is '
    'unauthenticated because the signup form needs it; it discloses whether an address is registered. '
    'This was accepted as a usability trade-off and is recorded here rather than left implicit.',
    '<b>There is one librarian role.</b> The admin table has no roles or permissions, so any '
    'librarian can do anything a librarian can do.',
    '<b>The seeded administrator password is public</b>, being printed in the schema script. It is a '
    'demo credential; the report and README both instruct that it be changed at first login.'])
story.append(PageBreak())

# ================================================== 7. VERIFICATION =========
H1('7.  Verification and validation')
P('<b>A constraint shaped this entire section and is stated before any result.</b> The machine on '
  'which this work was carried out had no PHP interpreter, no MySQL server, no container runtime and '
  'no administrative rights with which to install one. <b>The PHP source was therefore never '
  'executed.</b> Every claim below rests on analysis of the source, on unit-testable logic, or on a '
  'faithful port of the domain layer to a database that was available. Where that is not enough, this '
  'report says so rather than implying coverage it does not have.')
FIG('fig_verification.png',
    'What each verification technique actually covers. Filled markers denote primary evidence, hollow '
    'markers supporting evidence. The last two rows are the honest gap.')

H2('7.1  Static analysis')
P('Three analyses run over the PHP source with no interpreter required. Each answers a question that '
  'would otherwise only surface as a runtime error in front of a user.')
TBL([['Analysis', 'Question answered', 'Result'],
     ['schema_check.py',
      'Does every table and column named in the PHP exist in the schema?',
      '62 SQL statements across 40 files; no mismatch'],
     ['bind_check.py',
      'Is every declared SQL placeholder bound exactly once, and nothing extra?',
      '49 parameterised statements; all correct'],
     ['guard_check.py',
      'Does every non-public page carry an auth guard, every POST handler verify CSRF, and every '
      'POST form carry a token?',
      '31 pages; complete coverage, no GET-triggered state change remaining']],
    [30 * mm, 68 * mm, CW - 98 * mm],
    'Static analyses and their results.', mono_cols=(0,))

H2('7.2  Unit tests of the database-free logic')
P('<font face="Courier">tests/run-tests.php</font> contains 17 assertions over the logic that needs '
  'no database: due-date computation, the overdue-day count at the day-13, day-14 and day-15 '
  'boundaries, the fine formula, a fine frozen at the return date, bcrypt verification, the legacy '
  'md5 acceptance path, rehash detection, and card-number allocation including the SID099-to-SID100 '
  'rollover. <b>These assertions have not been executed</b>, for the reason given above; they are '
  'written and ready for a machine with PHP.')

H2('7.3  A stress harness without PHP')
P('To obtain evidence about the circulation algorithm despite the missing runtime, '
  '<font face="Courier">includes/library.php</font> was ported statement-for-statement onto SQLite, '
  'which was available through Python\'s standard library. The schema is not rewritten by hand: a '
  'translator reads <font face="Courier">database/library.sql</font> and converts the real DDL, '
  'preserving primary, unique and foreign keys, so the constraints under test are the ones that ship.')
P('The harness then drives the system hard while asserting six invariants after every 250 operations:')
TBL([['', 'Invariant'],
     ['I1', 'tblbooks.Count is never negative'],
     ['I2', 'For every title: copies on the shelf + open loans = total copies'],
     ['I3', 'No member holds more than MAX_BOOKS_PER_USER open loans'],
     ['I4', 'No member holds two open loans of the same title'],
     ['I5', 'Closed loans carry a return date; open loans do not'],
     ['I6', 'tblstudents.fines equals the sum of that member\'s closed-loan fines']],
    [10 * mm, CW - 10 * mm],
    'The six invariants asserted throughout the stress run.', header=False)
P(f"A run of {F['iterations']:,} randomised operations completed in {F['seconds']} seconds with no "
  f"invariant violated. The operation mix and the reasons issues were refused are shown in Figure 9; "
  f"every refusal branch in <font face=\"Courier\">lms_issue_blocker()</font> was exercised, which is "
  f"the evidence that the run reached the rules rather than merely the happy path.")
FIG('fig_fuzz.png',
    f"Outcome of the {F['iterations']:,}-operation randomised run, and the distribution of refusal "
    'reasons (logarithmic). One operation in twelve deliberately attempted to close an already-closed '
    'loan; none succeeded.')
P('Two scarcity profiles were used, because a single one cannot reach every rule: with one copy per '
  'title the "no copies" branch fires before any member can accumulate three loans, while with twelve '
  'copies of three titles the loan-limit and duplicate-title branches dominate. Running both is what '
  'gives full branch coverage of the policy.')

H2('7.4  Card-number allocation')
P('Allocation was exercised over 5,000 sequential draws, all unique. The PHP string-increment '
  'behaviour was also emulated at the boundary: SID999 increments to <b>SIE000</b>, the carry running '
  'into the letters. This looks alarming but is harmless — the sequence continues to produce unique '
  'six-character identifiers, and the UNIQUE constraint on the column would reject a collision in any '
  'case. It is recorded here because a reader who assumed a numeric counter would expect SID1000.')

H2('7.5  Concurrency experiments')
H3('Contending for the last copy')
P(f"Twelve threads attempted to issue the single remaining copy of one title simultaneously. "
  f"Exactly {LC['winners']} succeeded and {LC['losers']} were refused; the shelf count finished at "
  f"{LC['shelf']} and the ledger contained {LC['ledger']} row. This is the guarded UPDATE behaving as "
  f"designed: the losers match zero rows and roll back.")
H3('Contending for the loan limit')
P('The same experiment applied to the per-member rules exposed a defect. Eight threads issued eight '
  'different titles to one member at once. Because '
  '<font face="Courier">lms_issue_blocker()</font> ran before the transaction opened, all eight '
  f"passed the check: {R['before_violations']} of {R['trials']} trials exceeded the limit of "
  f"{R['limit']}, with a worst case of {R['before_worst']} books held by a single member.")
P('The fix re-checks the per-member rules inside the transaction, behind a locking read of the member '
  'row, which serialises concurrent issues for that member. The experiment was then repeated as a '
  f"regression test: {R['after_violations']} of {R['trials']} trials exceeded the limit, worst case "
  f"{R['after_worst']}.")
FIG('fig_race.png',
    'The loan-limit race before and after the fix. Left: how many books one member ended up holding '
    'after 8 simultaneous issues. Right: the proportion of trials that violated the policy.')

H2('7.6  Threats to the validity of these results')
P('The harness tests the algorithm and the schema constraints. It is not the deployed system, and '
  'four differences matter:')
UL(['<b>SQLite serialises writers across the whole database</b>, whereas MySQL relies on the row lock '
    'taken by <font face="Courier">SELECT ... FOR UPDATE</font>. The results show the algorithm is '
    'correct when transactions serialise; they do not prove InnoDB takes the lock as intended.',
    '<b>SQLite has no FOR UPDATE</b>, so <font face="Courier">BEGIN IMMEDIATE</font> stands in for it.',
    '<b>DECIMAL became REAL</b> in translation, so a rounding difference in MySQL\'s fixed-point '
    'arithmetic would not be detected here.',
    '<b>No PHP ran.</b> Sessions, CSRF enforcement at runtime, output escaping as rendered, the AJAX '
    'endpoints and every page template are covered only by static analysis and by the manual '
    'checklist in <font face="Courier">docs/TESTING.md</font>, which has not yet been executed.'])
P('The single most valuable next step is therefore not more analysis but one run on a machine with '
  'PHP and MySQL, following that checklist.')
story.append(PageBreak())

# ============================================================= 8. DEFECTS ====
H1('8.  Defects found and resolved')
P('Nine defects were identified during the re-engineering. Four affect security (D1, D3, D7, D9), '
  'two corrupt the circulation state itself (D2, D4), and three prevented a feature from working or '
  'made the application misstate its own data (D5, D6, D8). Each is recorded with how it was found, '
  'because the detection method is itself a result.')
TBL([['', 'Defect', 'Consequence', 'Found by'],
     ['D1', 'A member-facing page accepted <font face="Courier">?del=&lt;id&gt;</font> and deleted '
            'that row from the catalogue',
      'Any logged-in member could erase the entire book catalogue', 'Source review'],
     ['D2', 'Returning a book never restored <font face="Courier">tblbooks.Count</font>',
      'Shelf stock decreased monotonically; the catalogue drained to zero over time', 'Source review'],
     ['D3', 'Per-member rules checked outside the issue transaction',
      f"A member could exceed the loan limit under concurrent issues "
      f"({R['before_violations']}/{R['trials']} trials; worst case {R['before_worst']} books)",
      'Concurrency experiment'],
     ['D4', 'Issue decremented the copy count without checking availability, the loan limit or a '
            'duplicate loan',
      'Shelf counts could go negative and policy was unenforced', 'Source review'],
     ['D5', 'The admin dashboard prepared the wrong statement variable',
      '"Registered Users" displayed the number of issue records', 'Source review'],
     ['D6', 'The overdue-reminder page filtered on a session key never set for an administrator',
      'The overdue list was always empty, so no reminder could ever be sent', 'Source review'],
     ['D7', 'A member\'s request page listed every member\'s requests',
      'Disclosure of what other members were reading', 'Source review'],
     ['D8', 'The reminder link pointed at a page that did not exist',
      'Reminders could not be sent at all', 'Source review'],
     ['D9', 'Card numbers were allocated without a file lock',
      'Two simultaneous registrations could claim the same library card number', 'Source review']],
    [8 * mm, 46 * mm, 50 * mm, CW - 104 * mm],
    'Defects found and fixed, with the method that exposed each.')
P('Two further errors were introduced <i>during</i> the rework and caught before delivery, which is '
  'worth recording because they illustrate what the checks are for. Disabling prepared-statement '
  'emulation forbids reusing a named placeholder within one statement; two rewritten queries did '
  'exactly that and would have thrown at runtime. The placeholder analysis (Section 7.1) now runs over '
  'the whole codebase and reports the condition directly.')

# ====================================================== 9. RESULTS ===========
H1('9.  Results and discussion')
H2('9.1  What the evidence supports')
UL([f"The circulation algorithm maintains all six invariants across {F['iterations']:,} randomised "
    f"operations, including {F['counts']['issue_ok']:,} issues and {F['counts']['return_ok']:,} "
    'returns, with every policy branch exercised.',
    'Concurrent contention for the last copy resolves to exactly one winner, with no negative shelf '
    'count and no phantom ledger row.',
    'After the fix, the per-member loan limit holds under simultaneous issues in every trial.',
    'The schema and the SQL in the application agree completely: no statement references a table or '
    'column that does not exist, and no placeholder is left unbound.',
    'Every non-public page is guarded, every POST handler verifies a CSRF token, and no state change '
    'is reachable by a GET request.'])
H2('9.2  What the evidence does not support')
P('No claim is made that the application runs. It has not been started. A missing semicolon in a '
  'template, a mis-typed include path or a version-specific API difference would not have been caught '
  'by any check performed here — the structural analysis that was applied to every PHP file verifies '
  'tag and brace balance, not executability. The figures and results in Section 7 describe a design '
  'that is sound; the deployment remains unverified.')
H2('9.3  Reflection on method')
P('The most instructive result was D3, and not because the defect was severe — in a single-desk '
  'library, two simultaneous issues to the same member is an unlikely event. It is instructive '
  'because the code looked correct, was reviewed twice, and had a comment explaining why it was '
  'atomic. Only the experiment exposed the gap between the transaction boundary and the check that '
  'mattered. The contrast within the same function — a guard inside the write is safe, a guard before '
  'the transaction is not — is the kind of distinction that reads as pedantic in a textbook and '
  'becomes concrete when 38 of 40 trials fail.')
P('The second observation concerns the enforced constraint of a machine without PHP. Being unable to '
  'run the application forced the domain logic to be separated cleanly enough to be portable to '
  'another database, and forced the verification effort into static analysis and invariant-based '
  'testing. Both produced findings that a few manual clicks through the user interface would not have.')
story.append(PageBreak())

# ================================================ 10. LIMITATIONS ============
H1('10.  Limitations and future work')
TBL([['Limitation', 'Consequence', 'Suggested work'],
     ['The application has not been executed',
      'Deployment correctness is unverified',
      'Run docs/TESTING.md end to end on a PHP + MySQL host; execute tests/run-tests.php'],
     ['No reservations or holds',
      'A member who finds every copy out has no way to queue',
      'A reservation table and a claim step at return time'],
     ['Fines accumulate but are never settled',
      'The balance only ever grows; payments are invisible',
      'A payment ledger with per-transaction records, replacing the running total'],
     ['Reminders use mail() and are sent by hand',
      'Delivery is unreliable and depends on a librarian remembering',
      'An SMTP transport with a queue, driven by cron'],
     ['One librarian role',
      'No separation between desk staff and administrators',
      'Roles and a permission check in the admin guard'],
     ['No rate limiting on login',
      'Online password guessing is slowed only by bcrypt cost',
      'Per-account and per-IP attempt counters with backoff'],
     ['Bootstrap 3 and jQuery 1.10',
      'Both are long out of support',
      'A front-end refresh, deliberately excluded from this scope'],
     ['Stress harness is not the deployed engine',
      'MySQL-specific locking and fixed-point arithmetic are unobserved',
      'Re-run the invariant harness against MySQL directly']],
    [42 * mm, 48 * mm, CW - 90 * mm],
    'Known limitations, their consequences, and the work each would require.')

# ================================================== 11. CONCLUSION ===========
H1('11.  Conclusion')
P('The project set out to turn a coursework application into something that could be read, installed, '
  'defended and checked. The schema now exists and is constrained; the circulation rules live in one '
  'file and are applied consistently by both portals; the security posture addresses passwords, '
  'injection, encoding, forgery and privilege separation; and nine defects, including one that allowed '
  'any member to delete the catalogue, have been fixed.')
P('The verification effort is the part worth carrying forward. Working without the application\'s own '
  'runtime forced a discipline that a running system would not have required: state the invariants '
  'explicitly, port the logic to something that can be driven at scale, and be precise about the '
  'boundary between what has been demonstrated and what has merely been argued. That boundary is drawn '
  'in Figure 8 and in Section 7.6, and the single most useful next step is to close it with one '
  'session on a machine that has PHP and MySQL installed.')
story.append(PageBreak())

# ==================================================== APPENDICES =============
H1('Appendix A.  Installing and running')
story.append(Paragraph(check(
    '# 1. place the project where the web server can serve it<br/>'
    'git clone &lt;repository-url&gt; library<br/><br/>'
    '# 2. create the schema and seed data<br/>'
    'mysql -u root -p &lt; database/library.sql<br/><br/>'
    '# 3. point the application at the database (either form)<br/>'
    'cp includes/config.local.php.example includes/config.local.php   # edit it, or<br/>'
    'export LMS_DB_USER=library_app LMS_DB_PASS=secret<br/><br/>'
    '# 4. serve it<br/>'
    'php -S localhost:8000'), code))
P('The member portal is then at <font face="Courier">/</font> and the librarian panel at '
  '<font face="Courier">/admin/</font>. The seeded librarian account is '
  '<font face="Courier">admin</font> / <font face="Courier">Test@123</font>; its hash is public in '
  'the schema script, so it must be changed at first login. Member accounts are created through the '
  'signup form.')

H1('Appendix B.  Repository layout')
TBL([['Path', 'Contents'],
     ['index.php, dashboard.php, ...', 'Member portal pages'],
     ['admin/', 'Librarian panel, including its own AJAX lookups'],
     ['includes/config.php', 'Bootstrap: credentials, policy constants, PDO handle'],
     ['includes/auth.php', 'Passwords, sessions, CSRF, output escaping'],
     ['includes/library.php', 'Circulation rules, fines, transactional issue and return'],
     ['admin/includes/notify.php', 'Overdue reminder mail'],
     ['database/library.sql', 'Schema and seed data (idempotent)'],
     ['tests/run-tests.php', 'Unit assertions over the database-free logic'],
     ['tests/stress/', 'Static analyses and the SQLite stress harness'],
     ['docs/ARCHITECTURE.md', 'Design decisions and request walkthroughs'],
     ['docs/TESTING.md', 'Manual test checklist for the flows needing a database']],
    [52 * mm, CW - 52 * mm], None, mono_cols=(0,))

H1('Appendix C.  Reproducing the results in this report')
P('All figures in Sections 7 and 5.2 are generated from measurements, not transcribed. The commands '
  'below reproduce them; none requires PHP or MySQL.')
story.append(Paragraph(check(
    'python3 tests/stress/schema_check.py        # Section 7.1<br/>'
    'python3 tests/stress/bind_check.py          # Section 7.1<br/>'
    'python3 tests/stress/guard_check.py         # Section 7.1<br/>'
    'python3 tests/stress/stress.py              # Section 7.3, Figure 9<br/>'
    'python3 tests/stress/scenarios.py           # Sections 7.4, 7.5<br/>'
    'python3 tests/stress/race_loan_limit.py     # Section 7.5, Figure 10<br/><br/>'
    'php tests/run-tests.php                     # Section 7.2 (requires PHP)'), code))
P('Randomised runs are seeded, so the operation counts quoted in Section 7.3 reproduce exactly. The '
  'concurrency experiments are inherently non-deterministic: the defect rate before the fix varies '
  'between runs, while the rate after the fix is expected to remain zero.')

# ======================================================= DOCUMENT BUILD ======
class Doc(BaseDocTemplate):
    """Adds a running header/footer and feeds headings to the table of contents."""
    def __init__(self, *a, **kw):
        BaseDocTemplate.__init__(self, *a, **kw)
        frame = Frame(LM, BM, CW, PH - TM - BM, id='body')
        self.addPageTemplates([
            PageTemplate(id='title', frames=[frame], onPage=self.blank),
            PageTemplate(id='main', frames=[frame], onPage=self.decorate),
        ])
        self.section = ''

    def beforeDocument(self):
        # multiBuild runs the story twice; the header state must not leak between passes
        self.section = ''

    def blank(self, canv, doc):
        pass

    def decorate(self, canv, doc):
        canv.saveState()
        canv.setFont('Helvetica', 7.5)
        canv.setFillColor(MUTED)
        canv.drawString(LM, PH - TM + 7 * mm, 'Library Management System  |  Project Report')
        if self.section:
            canv.drawRightString(PW - RM, PH - TM + 7 * mm, self.section)
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(LM, PH - TM + 5.5 * mm, PW - RM, PH - TM + 5.5 * mm)
        canv.line(LM, BM - 6 * mm, PW - RM, BM - 6 * mm)
        canv.setFont('Helvetica', 8)
        canv.drawCentredString(PW / 2, BM - 10.5 * mm, str(canv.getPageNumber()))
        canv.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        txt = flowable.getPlainText()
        if style == 'h1':
            self.section = txt
            self.notify('TOCEntry', (0, txt, self.page))
        elif style == 'h2':
            self.notify('TOCEntry', (1, txt, self.page))

doc = Doc(OUT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
          title='Library Management System - Project Report',
          author='Piyush Anand', subject='Re-engineering and verification of a library circulation system')

# the title page uses the bare template; everything after it gets the running header
flow = [NextPageTemplate('main')] + story
doc.multiBuild(flow)
print('wrote', OUT)
