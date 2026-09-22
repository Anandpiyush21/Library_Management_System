<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();
require_once __DIR__ . '/includes/notify.php';

$sent = '';

if (isset($_POST['remind'])) {
    lms_csrf_verify();
    $studentId = trim($_POST['studentid'] ?? '');
    $sent = lms_send_overdue_reminder($dbh, $studentId)
        ? 'Reminder sent to ' . $studentId . '.'
        : 'Could not send the reminder to ' . $studentId . ' — see the PHP error log.';
}

// Every member holding a book past its due date, with the loan count and the
// fine accrued so far.  The previous version filtered on $_SESSION['stdid'],
// a key that is never set for an admin session, so the list was always empty.
$sql = "SELECT s.StudentId, s.FullName, s.EmailId,
               COUNT(*) AS OverdueCount, MIN(i.IssuesDate) AS OldestIssue
        FROM tblissuedbookdetails i
        JOIN tblstudents s ON s.StudentId = i.StudentID
        WHERE i.RetrunStatus = 0
          AND i.IssuesDate <= DATE_SUB(NOW(), INTERVAL :loandays DAY)
        GROUP BY s.StudentId, s.FullName, s.EmailId
        ORDER BY OldestIssue";
$query = $dbh->prepare($sql);
$query->execute([':loandays' => LOAN_PERIOD_DAYS]);
$results = $query->fetchAll();
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Overdue Reminders</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- FONT AWESOME STYLE  -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- DATATABLE STYLE  -->
    <link href="assets/js/dataTables/dataTables.bootstrap.css" rel="stylesheet" />
    <!-- CUSTOM STYLE  -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- GOOGLE FONT -->
    <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />

</head>
<body>
<?php include('includes/header.php');?>
        <div class="container">
            <!-- Your existing container content -->
            <div class="row">
                <div class="col-md-12">
                    <h4 class="header-line">Overdue Loans</h4>
                    <p class="text-muted">
                        Members holding a book beyond the <?php echo e(LOAN_PERIOD_DAYS); ?>-day loan
                        period. A fine of INR <?php echo e(number_format(FINE_PER_DAY, 2)); ?> per day
                        is accruing on each of these loans.
                    </p>
                    <?php if ($sent !== '') { ?>
                        <div class="alert alert-info"><?php echo e($sent); ?></div>
                    <?php } ?>
                    <table class="table table-striped table-bordered">
                        <thead>
                            <tr>
                                <th>Member</th>
                                <th>E-mail</th>
                                <th>Books Overdue</th>
                                <th>Oldest Loan</th>
                                <th>Fine so far (INR)</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($results as $row) { ?>
                                <tr>
                                    <td><?php echo e($row->FullName); ?> (<?php echo e($row->StudentId); ?>)</td>
                                    <td><?php echo e($row->EmailId); ?></td>
                                    <td><?php echo e($row->OverdueCount); ?></td>
                                    <td>
                                        <?php echo e($row->OldestIssue); ?>
                                        &mdash; <?php echo e(lms_days_overdue($row->OldestIssue)); ?> day(s) overdue
                                    </td>
                                    <td><?php echo e(number_format(lms_calculate_fine($row->OldestIssue), 2)); ?></td>
                                    <td>
                                        <form method="post" style="display:inline">
                                            <?php echo lms_csrf_field(); ?>
                                            <input type="hidden" name="studentid" value="<?php echo e($row->StudentId); ?>" />
                                            <button type="submit" name="remind" class="btn btn-warning btn-xs">
                                                <i class="fa fa-envelope"></i> Send Reminder
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                            <?php } ?>
                            <?php if (!$results) { ?>
                                <tr><td colspan="6" class="text-center">Nothing is overdue right now.</td></tr>
                            <?php } ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
       
    <!-- CORE JQUERY  -->
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
    <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
    <?php include('includes/footer.php');?>
    </body>
    </html>
