<?php
/**
 * Dependency-free test runner for the pure domain logic.
 *
 *     php tests/run-tests.php
 *
 * Only the functions that need no database are covered here: the loan-policy
 * calculations, the password layer and the card-number allocator. Everything
 * that touches PDO is exercised through the UI checklist in docs/TESTING.md.
 */

define('LOAN_PERIOD_DAYS', 14);
define('FINE_PER_DAY', 5.00);
define('MAX_BOOKS_PER_USER', 3);

require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/library.php';

$passed = 0;
$failed = 0;

function check(string $name, $expected, $actual): void
{
    global $passed, $failed;
    if ($expected === $actual) {
        $passed++;
        echo "  ok   $name\n";
    } else {
        $failed++;
        echo "  FAIL $name\n";
        echo "       expected: " . var_export($expected, true) . "\n";
        echo "       actual:   " . var_export($actual, true) . "\n";
    }
}

function daysAgo(int $n): string
{
    return (new DateTimeImmutable("-{$n} days"))->format('Y-m-d H:i:s');
}

echo "Loan period and due dates\n";
check('due date is issue date + loan period',
    (new DateTimeImmutable(daysAgo(0)))->modify('+14 days')->format('Y-m-d'),
    lms_due_date(daysAgo(0))->format('Y-m-d'));

echo "\nOverdue calculation\n";
check('a fresh loan is not overdue',            0,  lms_days_overdue(daysAgo(1)));
check('a loan on its due date is not overdue',  0,  lms_days_overdue(daysAgo(14)));
check('one day past the due date',              1,  lms_days_overdue(daysAgo(15)));
check('ten days past the due date',            10,  lms_days_overdue(daysAgo(24)));

echo "\nFine calculation\n";
check('no fine within the loan period',       0.0,  lms_calculate_fine(daysAgo(10)));
check('one overdue day costs FINE_PER_DAY',   5.0,  lms_calculate_fine(daysAgo(15)));
check('five overdue days',                   25.0,  lms_calculate_fine(daysAgo(19)));
check('fine is frozen at the return date',    5.0,  lms_calculate_fine(daysAgo(30), daysAgo(15)));

echo "\nPassword layer\n";
$hash = lms_hash_password('Test@123');
check('bcrypt hash verifies',                true,  lms_verify_password('Test@123', $hash));
check('wrong password is rejected',          false, lms_verify_password('wrong', $hash));
check('legacy md5 digest still verifies',    true,  lms_verify_password('Test@123', md5('Test@123')));
check('legacy md5 is flagged for rehash',    true,  lms_password_needs_rehash(md5('Test@123')));
check('a fresh bcrypt hash is not rehashed', false, lms_password_needs_rehash($hash));

echo "\nCard number allocation\n";
$counter = tempnam(sys_get_temp_dir(), 'sid');
file_put_contents($counter, 'SID016');
check('counter increments',      'SID017', lms_next_student_id($counter));
check('counter is persisted',    'SID018', lms_next_student_id($counter));
check('counter rolls over',      'SID100', (function () use ($counter) {
    file_put_contents($counter, 'SID099');
    return lms_next_student_id($counter);
})());
unlink($counter);

echo "\n" . str_repeat('-', 46) . "\n";
echo "$passed passed, $failed failed\n";
exit($failed === 0 ? 0 : 1);
