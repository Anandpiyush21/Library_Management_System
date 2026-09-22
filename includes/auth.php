<?php
/**
 * Authentication, session and output-escaping helpers.
 *
 * Passwords are stored as bcrypt hashes.  Accounts created by earlier
 * versions of this project hold unsalted md5 digests; those are accepted once
 * and transparently re-hashed on the next successful login, so no password
 * reset is needed when upgrading an existing installation.
 */

/** Start a session with hardened cookie flags (idempotent). */
function lms_session_start(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }
    session_set_cookie_params([
        'httponly' => true,
        'samesite' => 'Lax',
        'secure'   => !empty($_SERVER['HTTPS']),
    ]);
    session_start();
}

/** Hash a plaintext password for storage. */
function lms_hash_password(string $plain): string
{
    return password_hash($plain, PASSWORD_DEFAULT);
}

/** Verify a password against a bcrypt hash, or a legacy 32-char md5 digest. */
function lms_verify_password(string $plain, string $stored): bool
{
    if (preg_match('/^[a-f0-9]{32}$/i', $stored)) {
        return hash_equals(strtolower($stored), md5($plain));
    }
    return password_verify($plain, $stored);
}

/** True when a stored hash should be replaced (legacy md5 or outdated cost). */
function lms_password_needs_rehash(string $stored): bool
{
    return preg_match('/^[a-f0-9]{32}$/i', $stored) === 1
        || password_needs_rehash($stored, PASSWORD_DEFAULT);
}

/** Rewrite a stored hash after a successful login with a legacy password. */
function lms_upgrade_password(PDO $dbh, string $table, string $column, string $key, string $plain): void
{
    $sql = "UPDATE {$table} SET Password = :pwd WHERE {$column} = :key";
    $stmt = $dbh->prepare($sql);
    $stmt->execute([':pwd' => lms_hash_password($plain), ':key' => $key]);
}

/** Per-session CSRF token, created on first use. */
function lms_csrf_token(): string
{
    lms_session_start();
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

/** Hidden input carrying the CSRF token; drop it inside every POST form. */
function lms_csrf_field(): string
{
    return '<input type="hidden" name="csrf_token" value="' . lms_csrf_token() . '" />';
}

/** Abort the request unless the submitted token matches the session token. */
function lms_csrf_verify(): void
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        return;
    }
    $sent = $_POST['csrf_token'] ?? '';
    if (!is_string($sent) || !hash_equals($_SESSION['csrf_token'] ?? '', $sent)) {
        http_response_code(400);
        exit('Invalid or expired form token. Please reload the page and try again.');
    }
}

/** Redirect anonymous visitors to the student login page. */
function lms_require_student(string $loginPage = 'index.php'): string
{
    lms_session_start();
    if (empty($_SESSION['login']) || empty($_SESSION['stdid'])) {
        header('location:' . $loginPage);
        exit();
    }
    return $_SESSION['stdid'];
}

/** Redirect anonymous visitors to the admin login page. */
function lms_require_admin(string $loginPage = 'index.php'): string
{
    lms_session_start();
    if (empty($_SESSION['alogin'])) {
        header('location:' . $loginPage);
        exit();
    }
    return $_SESSION['alogin'];
}

/** Escape a value for safe interpolation into HTML. */
function e($value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
