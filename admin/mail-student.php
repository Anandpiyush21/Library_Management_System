<?php
session_start();
error_reporting(0);
include('includes/config.php');

if (strlen($_SESSION['alogin']) == 0) {
    header('location:index.php');
} else {
    include('includes/config.php');

    $sid = $_SESSION['stdid'];
    $rsts = 0;

    // Fetch students who haven't returned books for 6 days
    $sql = "SELECT DISTINCT sd.StudentId, sd.EmailId FROM tblissuedbookdetails ibd 
    JOIN tblstudents sd ON ibd.StudentID = sd.StudentId 
    WHERE ibd.StudentID=:sid AND ibd.RetrunStatus=:rsts 
    AND ibd.IssuesDate <= DATE_SUB(NOW(), INTERVAL 6 DAY)";
    $query = $dbh->prepare($sql);
    $query->bindParam(':sid', $sid, PDO::PARAM_STR);
    $query->bindParam(':rsts', $rsts, PDO::PARAM_STR);
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
    <title>IIIT Raichur | Manage Authors</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- FONT AWESOME STYLE  -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- DATATABLE STYLE  -->
    <link href="assets/js/dataTables/dataTables.bootstrap.css" rel="stylesheet" />
    <!-- CUSTOM STYLE  -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- GOOGLE FONT -->
    <link href='http://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />

</head>
<body>
<?php include('includes/header.php');?>
        <div class="container">
            <!-- Your existing container content -->
            <div class="row">
                <div class="col-md-12">
                    <h4>Students Who Haven't Returned Books for 6 Days:</h4>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Student ID</th>
                                <th>Email</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($results as $row) { ?>
                                <tr>
                                    <td><?php echo htmlentities($row['StudentID']); ?></td>
                                    <td>
                                        <a href="send-email.php?sid=<?php echo htmlentities($row['StudentId']); ?>">
                                            Send Reminder
                                        </a>
                                    </td>
                                </tr>
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
    <?php
}
?>
