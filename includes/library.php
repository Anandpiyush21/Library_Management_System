<?php
/**
 * Circulation domain logic.
 *
 * Everything that encodes a library *rule* — how long a book may be kept, how
 * a fine accrues, whether a member may borrow another copy — lives here, so
 * the page scripts stay presentation code and the rules can be changed in one
 * place (the constants in includes/config.php).
 */

/** Due date of a loan issued at $issuedAt. */
function lms_due_date(string $issuedAt): DateTimeImmutable
{
    return (new DateTimeImmutable($issuedAt))->modify('+' . LOAN_PERIOD_DAYS . ' days');
}

/** Whole days a loan is past its due date; 0 while it is still within term. */
function lms_days_overdue(string $issuedAt, ?string $comparedTo = null): int
{
    $reference = new DateTimeImmutable($comparedTo ?: 'now');
    $due = lms_due_date($issuedAt);
    if ($reference <= $due) {
        return 0;
    }
    return (int) $due->diff($reference)->days;
}

/** Fine payable on a loan: FINE_PER_DAY for every day past the due date. */
function lms_calculate_fine(string $issuedAt, ?string $returnedAt = null): float
{
    return round(lms_days_overdue($issuedAt, $returnedAt) * FINE_PER_DAY, 2);
}

/** Copies of a title currently on the shelf. */
function lms_copies_available(PDO $dbh, int $bookId): int
{
    $stmt = $dbh->prepare('SELECT Count FROM tblbooks WHERE id = :id');
    $stmt->execute([':id' => $bookId]);
    $row = $stmt->fetch();
    return $row ? (int) $row->Count : 0;
}

/** Loans a member has not yet closed. */
function lms_open_loan_count(PDO $dbh, string $studentId): int
{
    $stmt = $dbh->prepare(
        'SELECT COUNT(*) AS n FROM tblissuedbookdetails WHERE StudentID = :sid AND RetrunStatus = 0'
    );
    $stmt->execute([':sid' => $studentId]);
    return (int) $stmt->fetch()->n;
}

/** True when the member already holds an open loan of this title. */
function lms_has_open_loan(PDO $dbh, string $studentId, int $bookId): bool
{
    $stmt = $dbh->prepare(
        'SELECT 1 FROM tblissuedbookdetails
         WHERE StudentID = :sid AND BookId = :bid AND RetrunStatus = 0 LIMIT 1'
    );
    $stmt->execute([':sid' => $studentId, ':bid' => $bookId]);
    return (bool) $stmt->fetchColumn();
}

/**
 * Decide whether a book may be issued to a member.
 *
 * @return string|null Null when the loan is allowed, otherwise the reason.
 */
function lms_issue_blocker(PDO $dbh, string $studentId, int $bookId): ?string
{
    $stmt = $dbh->prepare('SELECT Status FROM tblstudents WHERE StudentId = :sid');
    $stmt->execute([':sid' => $studentId]);
    $student = $stmt->fetch();

    if (!$student) {
        return 'No member exists with ID ' . $studentId . '.';
    }
    if ((int) $student->Status !== 1) {
        return 'This member account is blocked and cannot borrow books.';
    }
    if (lms_copies_available($dbh, $bookId) < 1) {
        return 'All copies of this title are currently on loan.';
    }
    if (lms_has_open_loan($dbh, $studentId, $bookId)) {
        return 'This member already holds a copy of this title.';
    }
    if (lms_open_loan_count($dbh, $studentId) >= MAX_BOOKS_PER_USER) {
        return 'This member has reached the limit of ' . MAX_BOOKS_PER_USER . ' books on loan.';
    }
    return null;
}

/**
 * Issue a book: write the ledger row and decrement the shelf count as one
 * atomic unit, so a crash between the two cannot lose a copy.
 *
 * lms_issue_blocker() runs before this and produces the message the librarian
 * reads, but its answer is only a snapshot: two issues for the same member
 * submitted at once can both pass it. The per-member rules are therefore
 * re-checked here, inside the transaction, behind a locking read of the member
 * row — which serialises every concurrent issue for that member. The shelf
 * count needs no such lock because its guard (`AND Count > 0`) is part of the
 * UPDATE itself.
 */
function lms_issue_book(PDO $dbh, string $studentId, int $bookId): bool
{
    $dbh->beginTransaction();
    try {
        $lock = $dbh->prepare('SELECT Status FROM tblstudents WHERE StudentId = :sid FOR UPDATE');
        $lock->execute([':sid' => $studentId]);
        $member = $lock->fetch();

        if (!$member || (int) $member->Status !== 1) {
            $dbh->rollBack();
            return false;
        }
        if (lms_has_open_loan($dbh, $studentId, $bookId)
            || lms_open_loan_count($dbh, $studentId) >= MAX_BOOKS_PER_USER) {
            $dbh->rollBack();
            return false;
        }

        $dec = $dbh->prepare('UPDATE tblbooks SET Count = Count - 1 WHERE id = :id AND Count > 0');
        $dec->execute([':id' => $bookId]);
        if ($dec->rowCount() === 0) {         // lost the race for the last copy
            $dbh->rollBack();
            return false;
        }
        $ins = $dbh->prepare(
            'INSERT INTO tblissuedbookdetails (StudentID, BookId) VALUES (:sid, :bid)'
        );
        $ins->execute([':sid' => $studentId, ':bid' => $bookId]);
        $dbh->commit();
        return true;
    } catch (PDOException $e) {
        $dbh->rollBack();
        error_log('Issue failed: ' . $e->getMessage());
        return false;
    }
}

/**
 * Return a book: close the ledger row, put the copy back on the shelf and add
 * the fine to the member's balance — again atomically.
 */
function lms_return_book(PDO $dbh, int $issueId, ?float $fineOverride = null): bool
{
    $dbh->beginTransaction();
    try {
        $stmt = $dbh->prepare(
            'SELECT BookId, StudentID, IssuesDate, RetrunStatus
             FROM tblissuedbookdetails WHERE id = :id FOR UPDATE'
        );
        $stmt->execute([':id' => $issueId]);
        $loan = $stmt->fetch();

        if (!$loan || (int) $loan->RetrunStatus === 1) {
            $dbh->rollBack();
            return false;
        }

        $fine = $fineOverride !== null ? $fineOverride : lms_calculate_fine($loan->IssuesDate);

        $close = $dbh->prepare(
            'UPDATE tblissuedbookdetails
             SET fine = :fine, RetrunStatus = 1, ReturnDate = NOW() WHERE id = :id'
        );
        $close->execute([':fine' => $fine, ':id' => $issueId]);

        $dbh->prepare('UPDATE tblbooks SET Count = Count + 1 WHERE id = :id')
            ->execute([':id' => $loan->BookId]);

        $dbh->prepare('UPDATE tblstudents SET fines = fines + :fine WHERE StudentId = :sid')
            ->execute([':fine' => $fine, ':sid' => $loan->StudentID]);

        $dbh->commit();
        return true;
    } catch (PDOException $e) {
        $dbh->rollBack();
        error_log('Return failed: ' . $e->getMessage());
        return false;
    }
}

/** Next library card number, allocated under an exclusive file lock. */
function lms_next_student_id(string $counterFile): string
{
    $fp = fopen($counterFile, 'c+');
    if ($fp === false) {
        throw new RuntimeException('Cannot open the student-ID counter file.');
    }
    flock($fp, LOCK_EX);
    $current = trim((string) stream_get_contents($fp)) ?: 'SID000';
    $current++;                                  // "SID016" -> "SID017"
    ftruncate($fp, 0);
    rewind($fp);
    fwrite($fp, $current);
    fflush($fp);
    flock($fp, LOCK_UN);
    fclose($fp);
    return $current;
}

/**
 * Flash messages: set on one request, rendered and cleared on the next.
 * Keys map to the Bootstrap alert class used to display them.
 */
function lms_flash_set(string $key, string $message): void
{
    lms_session_start();
    $_SESSION[$key] = $message;
}

function lms_flash_render(): string
{
    lms_session_start();
    $classes = [
        'msg'       => 'alert-success',
        'updatemsg' => 'alert-success',
        'delmsg'    => 'alert-success',
        'error'     => 'alert-danger',
    ];
    $html = '';
    foreach ($classes as $key => $class) {
        if (!empty($_SESSION[$key])) {
            $html .= '<div class="col-md-12"><div class="alert ' . $class . '">'
                   . e($_SESSION[$key]) . '</div></div>';
            unset($_SESSION[$key]);
        }
    }
    return $html;
}
