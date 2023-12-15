<?php
session_start();
include('includes/config.php');
error_reporting(0);
if (strlen($_SESSION['login']) == 0) {
    header('location:index.php');
} else {
    if (isset($_POST['submit'])) {
        $studentId = $_SESSION['stdid'];
        $bookTitle = $_POST['bookTitle'];
        $author = $_POST['author'];
        $suggestion = $_POST['suggestion']; // New variable to capture the suggestion

        // Insert the request into the tblrequest table
        $sql = "INSERT INTO tblrequest (StudentId, BookTitle, Author, Suggestion) VALUES (:studentId, :bookTitle, :author, :suggestion)";
        $query = $dbh->prepare($sql);
        $query->bindParam(':studentId', $studentId, PDO::PARAM_STR);
        $query->bindParam(':bookTitle', $bookTitle, PDO::PARAM_STR);
        $query->bindParam(':author', $author, PDO::PARAM_STR);
        $query->bindParam(':suggestion', $suggestion, PDO::PARAM_STR);
        $query->execute();

        echo '<script>alert("Your request has been submitted")</script>';
    }
    $sql = "SELECT * FROM tblrequest";
    $query = $dbh->prepare($sql);
    $query->execute();
    $results = $query->fetchAll(PDO::FETCH_ASSOC);
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
    <link href='http://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />

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
                            Existing Book Requests
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover">
                                    <thead>
                                        <tr>
                                            <th>Request ID</th>
                                            <th>Student ID</th>
                                            <th>Book Title</th>
                                            <th>Author</th>
                                            <th>Suggestion</th>
                                            <th>Approval Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($results as $row) { ?>
                                            <tr>
                                                <td><?php echo $row['RequestId']; ?></td>
                                                <td><?php echo $row['StudentId']; ?></td>
                                                <td><?php echo $row['BookTitle']; ?></td>
                                                <td><?php echo $row['Author']; ?></td>
                                                <td><?php echo $row['Suggestion']; ?></td>
                                                <td><?php echo $row['IsApproved']; ?></td>
                                            </tr>
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
<?php
}
?>
