<?php
require_once __DIR__ . '/includes/config.php';
$studentId = lms_require_student();

$error = '';
$msg   = '';

if (isset($_POST['submit'])) {
    lms_csrf_verify();
    $bookTitle  = trim($_POST['bookTitle'] ?? '');
    $author     = trim($_POST['author'] ?? '');
    $suggestion = trim($_POST['suggestion'] ?? '');

    if ($bookTitle === '' || $author === '') {
        $error = 'Please give both a title and an author.';
    } else {
        $sql = "INSERT INTO tblrequest (StudentId, BookTitle, Author, Suggestion, IsApproved)
                VALUES (:studentId, :bookTitle, :author, :suggestion, 'Pending')";
        $dbh->prepare($sql)->execute([
            ':studentId'  => $studentId,
            ':bookTitle'  => $bookTitle,
            ':author'     => $author,
            ':suggestion' => $suggestion,
        ]);
        $msg = 'Your acquisition request has been sent to the librarian.';
    }
}

// A member sees their own requests only — the earlier version listed every
// request in the system, which leaked what other members were reading.
$query = $dbh->prepare(
    "SELECT RequestId, BookTitle, Author, Suggestion, IsApproved, RequestDate
     FROM tblrequest WHERE StudentId = :sid ORDER BY RequestId DESC"
);
$query->execute([':sid' => $studentId]);
$results = $query->fetchAll();
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <!--[if IE]>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <![endif]-->
    <title>IIITR Library | Book Request</title>
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
                    <h4 class="header-line">Book Request</h4>
                </div>
            </div>
            <div class="row">
                <div class="col-md-9 col-md-offset-1">
                    <div class="panel panel-danger">
                        <div class="panel-heading">
                            Request a Book
                        </div>
                        <div class="panel-body">
                            <form name="bookrequest" method="post">
                                <?php echo lms_csrf_field(); ?>
                                <?php if ($error !== '') { ?>
                                    <div class="alert alert-danger"><?php echo e($error); ?></div>
                                <?php } elseif ($msg !== '') { ?>
                                    <div class="alert alert-success"><?php echo e($msg); ?></div>
                                <?php } ?>
                                <div class="form-group">
                                    <label>Book Title</label>
                                    <input class="form-control" type="text" name="bookTitle" required />
                                </div>

                                <div class="form-group">
                                    <label>Author</label>
                                    <input class="form-control" type="text" name="author" required />
                                </div>

                                <div class="form-group">
                                    <label>Suggestion</label>
                                    <textarea class="form-control" name="suggestion" required></textarea>
                                </div>

                                <button type="submit" name="submit" class="btn btn-primary">Submit Request</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
                    <!-- Display existing book requests -->
                    <div class="row">
                <div class="col-md-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            My Book Requests
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover">
                                    <thead>
                                        <tr>
                                            <th>Request ID</th>
                                            <th>Requested On</th>
                                            <th>Book Title</th>
                                            <th>Author</th>
                                            <th>Suggestion</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($results as $row) {
                                            $badge = $row->IsApproved === 'Approved' ? 'label-success'
                                                   : ($row->IsApproved === 'Not Approved' ? 'label-danger' : 'label-warning'); ?>
                                            <tr>
                                                <td><?php echo e($row->RequestId); ?></td>
                                                <td><?php echo e($row->RequestDate); ?></td>
                                                <td><?php echo e($row->BookTitle); ?></td>
                                                <td><?php echo e($row->Author); ?></td>
                                                <td><?php echo e($row->Suggestion); ?></td>
                                                <td><span class="label <?php echo $badge; ?>"><?php echo e($row->IsApproved); ?></span></td>
                                            </tr>
                                        <?php } ?>
                                        <?php if (!$results) { ?>
                                            <tr><td colspan="6" class="text-center">You have not requested any book yet.</td></tr>
                                        <?php } ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- End of existing book requests -->
        </div>
    </div>
    <!-- CONTENT-WRAPPER SECTION END-->
    <?php include('includes/footer.php'); ?>
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
    <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
</body>

</html>
