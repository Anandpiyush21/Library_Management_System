<?php
/**
 * AJAX endpoint: resolve an ISBN or title fragment to selectable copies.
 * Returns <option> elements for the book drop-down on issue-book.php.
 */
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

header('Content-Type: text/html; charset=utf-8');

$term = trim($_POST['bookid'] ?? '');
if ($term === '') {
    exit('<option class="others">Enter an ISBN number or a title</option>');
}

$query = $dbh->prepare(
    'SELECT id, BookName, ISBNNumber, Count FROM tblbooks
     WHERE ISBNNumber = :isbn OR BookName LIKE :title
     ORDER BY BookName LIMIT 25'
);
$query->execute([':isbn' => $term, ':title' => '%' . $term . '%']);
$books = $query->fetchAll();

if (!$books) {
    echo '<option class="others">No matching book in the catalogue</option>';
    echo '<script>$("#submit").prop("disabled", true);</script>';
    exit();
}

$anyAvailable = false;
foreach ($books as $book) {
    $available = (int) $book->Count > 0;
    $anyAvailable = $anyAvailable || $available;
    printf(
        '<option value="%s"%s>%s (ISBN %s) — %s</option>',
        e($book->id),
        $available ? '' : ' disabled',
        e($book->BookName),
        e($book->ISBNNumber),
        $available ? e($book->Count) . ' available' : 'all copies on loan'
    );
}

echo '<script>$("#submit").prop("disabled", ' . ($anyAvailable ? 'false' : 'true') . ');</script>';
