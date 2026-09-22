<?php
require_once __DIR__ . '/includes/config.php';
$studentId = lms_require_student();

// One pass over the member's ledger feeds every tile below.
$sql = "SELECT i.IssuesDate, i.RetrunStatus
        FROM tblissuedbookdetails i
        WHERE i.StudentID = :sid";
$query = $dbh->prepare($sql);
$query->execute([':sid' => $studentId]);
$loans = $query->fetchAll();

$totalIssued = count($loans);
$onLoan      = 0;
$overdue     = 0;
$accruing    = 0.0;

foreach ($loans as $loan) {
    if ((int) $loan->RetrunStatus === 0) {
        $onLoan++;
        if (lms_days_overdue($loan->IssuesDate) > 0) {
            $overdue++;
            $accruing += lms_calculate_fine($loan->IssuesDate);
        }
    }
}

$profile = $dbh->prepare("SELECT FullName, fines FROM tblstudents WHERE StudentId = :sid");
$profile->execute([':sid' => $studentId]);
$student = $profile->fetch();

$tiles = [
    ['alert-info',    'fa-book',           $totalIssued,                        'Books Borrowed (all time)'],
    ['alert-success', 'fa-bookmark',       $onLoan . ' / ' . MAX_BOOKS_PER_USER, 'Currently On Loan'],
    ['alert-warning', 'fa-clock-o',        $overdue,                            'Overdue Books'],
    ['alert-danger',  'fa-inr',            number_format((float) $student->fines + $accruing, 2), 'Fine Payable (INR)'],
];
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="Member dashboard" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Member Dashboard</title>
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
                    <h4 class="header-line">Welcome, <?php echo e($student->FullName); ?> (<?php echo e($studentId); ?>)</h4>
                </div>
            </div>

            <div class="row">
            <?php foreach ($tiles as $tile) {
                list($cls, $icon, $value, $label) = $tile; ?>
                <div class="col-md-3 col-sm-3 col-xs-6">
                    <div class="alert <?php echo $cls; ?> back-widget-set text-center">
                        <i class="fa <?php echo $icon; ?> fa-5x"></i>
                        <h3><?php echo e($value); ?></h3>
                        <?php echo e($label); ?>
                    </div>
                </div>
            <?php } ?>
            </div>

            <?php if ($overdue > 0) { ?>
            <div class="row">
                <div class="col-md-12">
                    <div class="alert alert-danger">
                        <strong>Please return your overdue books.</strong>
                        A fine of INR <?php echo e(number_format(FINE_PER_DAY, 2)); ?> per day accrues after the
                        <?php echo e(LOAN_PERIOD_DAYS); ?>-day loan period.
                        See <a href="issued-books.php">My Issued Books</a> for the details.
                    </div>
                </div>
            </div>
            <?php } ?>
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
