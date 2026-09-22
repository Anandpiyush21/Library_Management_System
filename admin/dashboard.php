<?php
require_once __DIR__ . '/includes/config.php';
$adminUser = lms_require_admin();

/**
 * One scalar query per tile. (The previous version prepared $sql1 while
 * meaning $sql3, so the "Registered Users" tile actually showed the number of
 * issue records.)
 */
function lms_scalar(PDO $dbh, string $sql, array $params = [])
{
    $stmt = $dbh->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchColumn();
}

$titles      = lms_scalar($dbh, 'SELECT COUNT(*) FROM tblbooks');
$copies      = lms_scalar($dbh, 'SELECT COALESCE(SUM(Count), 0) FROM tblbooks');
$members     = lms_scalar($dbh, 'SELECT COUNT(*) FROM tblstudents');
$blocked     = lms_scalar($dbh, 'SELECT COUNT(*) FROM tblstudents WHERE Status = 0');
$onLoan      = lms_scalar($dbh, 'SELECT COUNT(*) FROM tblissuedbookdetails WHERE RetrunStatus = 0');
$issuedTotal = lms_scalar($dbh, 'SELECT COUNT(*) FROM tblissuedbookdetails');
$pendingReq  = lms_scalar($dbh, "SELECT COUNT(*) FROM tblrequest WHERE IsApproved = 'Pending'");
$overdue     = lms_scalar(
    $dbh,
    'SELECT COUNT(*) FROM tblissuedbookdetails
     WHERE RetrunStatus = 0 AND IssuesDate <= DATE_SUB(NOW(), INTERVAL :d DAY)',
    [':d' => LOAN_PERIOD_DAYS]
);
$finesDue = lms_scalar($dbh, 'SELECT COALESCE(SUM(fines), 0) FROM tblstudents');

$tiles = [
    ['alert-success', 'fa-book',    $titles,                        'Titles in Catalogue',  'manage-books.php'],
    ['alert-info',    'fa-copy',    $copies,                        'Copies on Shelf',      'manage-books.php'],
    ['alert-info',    'fa-users',   $members,                       'Registered Members',   'reg-students.php'],
    ['alert-warning', 'fa-ban',     $blocked,                       'Blocked Members',      'reg-students.php'],
    ['alert-info',    'fa-exchange', $onLoan,                       'Books Currently Out',  'manage-issued-books.php?filter=open'],
    ['alert-danger',  'fa-clock-o', $overdue,                       'Overdue Loans',        'manage-issued-books.php?filter=overdue'],
    ['alert-warning', 'fa-inbox',   $pendingReq,                    'Pending Requests',     'book-request.php?status=Pending'],
    ['alert-danger',  'fa-inr',     number_format((float) $finesDue, 2), 'Fines Outstanding (INR)', 'reg-students.php'],
];
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta name="description" content="Librarian dashboard" />
  <meta name="author" content="" />
  <title>Library Management System | Admin Dashboard</title>
  <!-- BOOTSTRAP CORE STYLE  -->
  <link href="assets/css/bootstrap.css" rel="stylesheet" />
  <!-- FONT AWESOME STYLE  -->
  <link href="assets/css/font-awesome.css" rel="stylesheet" />
  <!-- CUSTOM STYLE  -->
  <link href="assets/css/style.css" rel="stylesheet" />
  <!-- GOOGLE FONT -->
  <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
</head>

<body>
  <!------MENU SECTION START-->
  <?php include('includes/header.php'); ?>
  <!-- MENU SECTION END-->
  <div class="content-wrapper">
    <div class="container">
      <div class="row pad-botm">
        <div class="col-md-12">
          <h4 class="header-line">Admin Dashboard &mdash; signed in as <?php echo e($adminUser); ?></h4>
        </div>
      </div>

      <div class="row"><?php echo lms_flash_render(); ?></div>

      <div class="row">
        <?php foreach ($tiles as $tile) {
          list($cls, $icon, $value, $label, $link) = $tile; ?>
          <div class="col-md-3 col-sm-3 col-xs-6">
            <a href="<?php echo $link; ?>" style="text-decoration:none">
              <div class="alert <?php echo $cls; ?> back-widget-set text-center">
                <i class="fa <?php echo $icon; ?> fa-5x"></i>
                <h3><?php echo e($value); ?></h3>
                <?php echo e($label); ?>
              </div>
            </a>
          </div>
        <?php } ?>
      </div>

      <div class="row">
        <div class="col-md-12">
          <div class="panel panel-default">
            <div class="panel-heading">Circulation policy in force</div>
            <div class="panel-body">
              <ul>
                <li>Loan period: <strong><?php echo e(LOAN_PERIOD_DAYS); ?> days</strong></li>
                <li>Fine after the due date: <strong>INR <?php echo e(number_format(FINE_PER_DAY, 2)); ?> per day</strong></li>
                <li>Maximum books per member: <strong><?php echo e(MAX_BOOKS_PER_USER); ?></strong></li>
                <li>Loans recorded all time: <strong><?php echo e($issuedTotal); ?></strong></li>
              </ul>
              <p class="text-muted">
                These values live in <code>includes/config.php</code> and are applied by
                <code>includes/library.php</code>, so changing one constant changes issuing,
                fines and reminders together.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- CONTENT-WRAPPER SECTION END-->
  <?php include('includes/footer.php'); ?>
  <!-- FOOTER SECTION END-->
  <script src="assets/js/jquery-1.10.2.js"></script>
  <script src="assets/js/bootstrap.js"></script>
  <script src="assets/js/custom.js"></script>
</body>

</html>
