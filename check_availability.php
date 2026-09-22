<?php
/**
 * AJAX endpoint: tell the signup form whether an e-mail is still free.
 */
require_once __DIR__ . '/includes/config.php';

header('Content-Type: text/html; charset=utf-8');

$email = trim($_POST['emailid'] ?? '');

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    exit('<span style="color:red"> Please enter a valid e-mail address.</span>');
}

$query = $dbh->prepare('SELECT 1 FROM tblstudents WHERE EmailId = :email LIMIT 1');
$query->execute([':email' => $email]);

if ($query->fetchColumn()) {
    echo '<span style="color:red"> This e-mail address is already registered.</span>';
    echo '<script>$("#submit").prop("disabled", true);</script>';
} else {
    echo '<span style="color:green"> This e-mail address is available.</span>';
    echo '<script>$("#submit").prop("disabled", false);</script>';
}
