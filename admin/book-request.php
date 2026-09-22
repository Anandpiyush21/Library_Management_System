<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

// Approving or denying an acquisition request is a state change, so both go
// through one CSRF-checked POST handler with a whitelisted decision value.
if (isset($_POST['decision'])) {
    lms_csrf_verify();
    $requestId = (int) ($_POST['request_id'] ?? 0);
    $decision  = $_POST['decision'] === 'approve' ? 'Approved' : 'Not Approved';

    $dbh->prepare('UPDATE tblrequest SET IsApproved = :status WHERE RequestId = :id')
        ->execute([':status' => $decision, ':id' => $requestId]);

    lms_flash_set('msg', 'Request #' . $requestId . ' marked as "' . $decision . '".');
    header('location:book-request.php');
    exit();
}

$status = $_GET['status'] ?? 'all';      // all | Pending | Approved | Not Approved
$sql = "SELECT r.RequestId, r.StudentId, r.BookTitle, r.Author, r.Suggestion,
               r.IsApproved, r.RequestDate, s.FullName
        FROM tblrequest r
        LEFT JOIN tblstudents s ON s.StudentId = r.StudentId
        ORDER BY r.RequestId DESC";
$query = $dbh->prepare($sql);
$query->execute();
$results = $query->fetchAll();
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>Requested Books | Admin Panel</title>
    <!-- Your CSS links -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- End of your CSS links -->
</head>
<body>
    <!-- Header section -->
    <?php include('includes/header.php'); ?>

    <div class="content-wrapper">
        <div class="container">
            <!-- Requested Books Display Section -->
            <div class="row">
                <div class="col-md-12">
                    <div class="panel panel-default">
                        <!-- Table to display all requested books -->
                        <div class="panel-heading">
                            All Requested Books &nbsp;|&nbsp;
                            <a href="?status=all">All</a> &middot;
                            <a href="?status=Pending">Pending</a> &middot;
                            <a href="?status=Approved">Approved</a> &middot;
                            <a href="?status=Not+Approved">Declined</a>
                        </div>
                        <?php echo lms_flash_render(); ?>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover">
                                    <!-- Table headers -->
                                    <thead>
                                        <tr>
                                            <th>Request ID</th>
                                            <th>Requested On</th>
                                            <th>Member</th>
                                            <th>Book Title</th>
                                            <th>Author</th>
                                            <th>Suggestion</th>
                                            <th>Status</th>
                                            <th>Decision</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($results as $row) {
                                            if ($status !== 'all' && $row->IsApproved !== $status) { continue; }
                                            $badge = $row->IsApproved === 'Approved' ? 'label-success'
                                                   : ($row->IsApproved === 'Not Approved' ? 'label-danger' : 'label-warning'); ?>
                                            <tr>
                                                <td><?php echo e($row->RequestId); ?></td>
                                                <td><?php echo e($row->RequestDate); ?></td>
                                                <td><?php echo e($row->FullName); ?> (<?php echo e($row->StudentId); ?>)</td>
                                                <td><?php echo e($row->BookTitle); ?></td>
                                                <td><?php echo e($row->Author); ?></td>
                                                <td><?php echo e($row->Suggestion); ?></td>
                                                <td><span class="label <?php echo $badge; ?>"><?php echo e($row->IsApproved); ?></span></td>
                                                <td>
                                                    <form method="post" style="display:inline">
                                                        <?php echo lms_csrf_field(); ?>
                                                        <input type="hidden" name="request_id" value="<?php echo e($row->RequestId); ?>" />
                                                        <button type="submit" name="decision" value="approve" class="btn btn-success btn-xs">Approve</button>
                                                    </form>
                                                    <form method="post" style="display:inline">
                                                        <?php echo lms_csrf_field(); ?>
                                                        <input type="hidden" name="request_id" value="<?php echo e($row->RequestId); ?>" />
                                                        <button type="submit" name="decision" value="deny" class="btn btn-danger btn-xs">Deny</button>
                                                    </form>
                                                </td>
                                            </tr>
                                        <?php } ?>
                                        <?php if (!$results) { ?>
                                            <tr><td colspan="8" class="text-center">No acquisition requests yet.</td></tr>
                                        <?php } ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- End Requested Books Display Section -->
        </div>
    </div>

    <!-- Footer -->
    <?php include('includes/footer.php'); ?>
    <!-- JavaScript links and scripts -->
</body>
</html>
