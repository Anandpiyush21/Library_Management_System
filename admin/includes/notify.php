<?php
/**
 * Overdue-reminder mail.
 *
 * Uses PHP's mail() so the project stays dependency-free; on a development
 * box without a configured MTA the call simply fails and is logged, which is
 * why the caller reports success or failure back to the librarian.
 */

/** Compose and send the overdue reminder for one member. */
function lms_send_overdue_reminder(PDO $dbh, string $studentId): bool
{
    $sql = "SELECT s.FullName, s.EmailId, b.BookName, i.IssuesDate
            FROM tblissuedbookdetails i
            JOIN tblstudents s ON s.StudentId = i.StudentID
            JOIN tblbooks b ON b.id = i.BookId
            WHERE i.StudentID = :sid AND i.RetrunStatus = 0
            ORDER BY i.IssuesDate";
    $query = $dbh->prepare($sql);
    $query->execute([':sid' => $studentId]);
    $loans = $query->fetchAll();

    if (!$loans) {
        return false;
    }

    $member = $loans[0];
    $lines  = [];
    $total  = 0.0;

    foreach ($loans as $loan) {
        $days = lms_days_overdue($loan->IssuesDate);
        if ($days === 0) {
            continue;
        }
        $fine   = lms_calculate_fine($loan->IssuesDate);
        $total += $fine;
        $lines[] = sprintf(
            ' - %s (issued %s, due %s): %d day(s) overdue, fine INR %s',
            $loan->BookName,
            (new DateTimeImmutable($loan->IssuesDate))->format('d M Y'),
            lms_due_date($loan->IssuesDate)->format('d M Y'),
            $days,
            number_format($fine, 2)
        );
    }

    if (!$lines) {
        return false;
    }

    $subject = 'Library reminder: ' . count($lines) . ' overdue book(s)';
    $body = "Dear " . $member->FullName . " (" . $studentId . "),\n\n"
          . "Our records show the following overdue loans:\n\n"
          . implode("\n", $lines) . "\n\n"
          . "Total fine accrued so far: INR " . number_format($total, 2) . "\n"
          . "Fines accrue at INR " . number_format(FINE_PER_DAY, 2) . " per day after the "
          . LOAN_PERIOD_DAYS . "-day loan period.\n\n"
          . "Please return the book(s) at your earliest convenience.\n\n"
          . "-- Library Management System (automated message)";

    $headers = 'From: ' . (getenv('LMS_MAIL_FROM') ?: 'library@localhost') . "\r\n"
             . "Content-Type: text/plain; charset=UTF-8\r\n";

    if (!@mail($member->EmailId, $subject, $body, $headers)) {
        error_log('Overdue reminder to ' . $member->EmailId . ' could not be sent.');
        return false;
    }
    return true;
}
