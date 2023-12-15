<?php
session_start();
error_reporting(0);
include('includes/config.php');

if (isset($_POST['deny'])) {
    $request_id = $_POST['request_id'];

    // Update the tblrequest table for denial
    $sql = "UPDATE tblrequest SET isApproved = 'Not Approved' WHERE RequestId = :request_id";
    $query = $dbh->prepare($sql);
    $query->bindParam(':request_id', $request_id, PDO::PARAM_INT);
    $query->execute();
    // Redirect to the previous page after update
    header('Location: book-request.php');
    exit();
}
if (isset($_POST['approve'])) {
    $request_id = $_POST['request_id'];

    // Update the tblrequest table for denial
    $sql = "UPDATE tblrequest SET isApproved = 'Approved' WHERE RequestId = :request_id";
    $query = $dbh->prepare($sql);
    $query->bindParam(':request_id', $request_id, PDO::PARAM_INT);
    $query->execute();
    // Redirect to the previous page after update
    header('Location: book-request.php');
    exit();
}

if(strlen($_SESSION['alogin'])==0) {   
    header('location:index.php');
} else {
    $studentId = $_SESSION['stdid'];
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
                        <div class="panel-heading">All Requested Books</div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover">
                                    <!-- Table headers -->
                                    <thead>
                                        <tr>
                                            <th>Request ID</th>
                                            <th>Student ID</th>
                                            <th>Book Title</th>
                                            <th>Author</th>
                                            <th>Curent Status</th>
                                            <!-- Add more columns as needed -->
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <!-- Loop through each requested book -->
                                        <?php foreach ($results as $row) { ?>
                                            <tr>
                                                <td><?php echo $row['RequestId']; ?></td>
                                                <td><?php echo $row['StudentId']; ?></td>
                                                <td><?php echo $row['BookTitle']; ?></td>
                                                <td><?php echo $row['Author']; ?></td>
                                                <td><?php echo $row['IsApproved']; ?></td>

                                           
                                                <td>
                                                <form action="book-request.php" method="post" style="display:inline;">
                                                    <input type="hidden" name="request_id" value="<?php echo $row['RequestId']; ?>">
                                                    <button type="submit" name="approve" class="btn btn-success">Approve</button>
                                                </form>

                                                <form action="book-request.php" method="post" style="display:inline;">
                                                    <input type="hidden" name="request_id" value="<?php echo $row['RequestId']; ?>">
                                                    <button type="submit" name="deny" class="btn btn-danger">Deny</button>
                                                </form>
                                            </td>
            </td>
                                            </tr>
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

<?php } ?>
