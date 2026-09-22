<?php
/**
 * Application bootstrap: configuration, database handle and shared helpers.
 *
 * Credentials are read from the environment first so that the same code can
 * run on a developer laptop, in a container and on a shared host without
 * editing tracked files.  A gitignored includes/config.local.php may override
 * any of the four constants below.
 */

if (is_readable(__DIR__ . '/config.local.php')) {
    require_once __DIR__ . '/config.local.php';
}

defined('DB_HOST') || define('DB_HOST', getenv('LMS_DB_HOST') ?: 'localhost');
defined('DB_USER') || define('DB_USER', getenv('LMS_DB_USER') ?: 'root');
defined('DB_PASS') || define('DB_PASS', getenv('LMS_DB_PASS') !== false ? getenv('LMS_DB_PASS') : '');
defined('DB_NAME') || define('DB_NAME', getenv('LMS_DB_NAME') ?: 'library');

// Circulation policy — see docs/ARCHITECTURE.md ("Business rules").
defined('LOAN_PERIOD_DAYS')  || define('LOAN_PERIOD_DAYS', 14);   // days a book may be kept
defined('FINE_PER_DAY')      || define('FINE_PER_DAY', 5.00);     // INR charged per overdue day
defined('MAX_BOOKS_PER_USER')|| define('MAX_BOOKS_PER_USER', 3);  // simultaneous open loans

// Show errors while developing, log them in production.
$lmsDebug = filter_var(getenv('LMS_DEBUG') ?: 'false', FILTER_VALIDATE_BOOLEAN);
ini_set('display_errors', $lmsDebug ? '1' : '0');
ini_set('log_errors', '1');
error_reporting($lmsDebug ? E_ALL : E_ALL & ~E_NOTICE & ~E_DEPRECATED);

try {
    $dbh = new PDO(
        'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
        DB_USER,
        DB_PASS,
        [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ]
    );
} catch (PDOException $e) {
    error_log('Database connection failed: ' . $e->getMessage());
    exit('The library service is temporarily unavailable. Please try again later.');
}

require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/library.php';
