<?php
/**
 * AJAX endpoint: look up a member by library card number.
 * Returns an HTML fragment that issue-book.php drops next to the ID field.
 */
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

header('Content-Type: text/html; charset=utf-8');

$studentid = strtoupper(trim($_POST['studentid'] ?? ''));
if ($studentid === '') {
    exit('<span style="color:red">Please enter a library card number.</span>');
}

$query = $dbh->prepare('SELECT FullName, Status FROM tblstudents WHERE StudentId = :studentid');
$query->execute([':studentid' => $studentid]);
$student = $query->fetch();

if (!$student) {
    echo '<span style="color:red">No member found with that card number.</span>';
    echo '<script>$("#submit").prop("disabled", true);</script>';
    exit();
}

if ((int) $student->Status !== 1) {
    echo '<span style="color:red">This member is blocked.</span><br />';
    echo '<b>Member:</b> ' . e($student->FullName);
    echo '<script>$("#submit").prop("disabled", true);</script>';
    exit();
}

$openLoans = lms_open_loan_count($dbh, $studentid);
echo '<b>Member:</b> ' . e($student->FullName)
   . ' &nbsp;<span class="text-muted">(' . $openLoans . ' of ' . MAX_BOOKS_PER_USER . ' books on loan)</span>';

if ($openLoans >= MAX_BOOKS_PER_USER) {
    echo '<br /><span style="color:red">Loan limit reached — a book must be returned first.</span>';
    echo '<script>$("#submit").prop("disabled", true);</script>';
} else {
    echo '<script>$("#submit").prop("disabled", false);</script>';
}
