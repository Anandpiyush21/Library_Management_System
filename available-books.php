<?php
session_start();
error_reporting(0);
include('includes/config.php');

if (strlen($_SESSION['login']) == 0) {
    header('location:index.php');
    exit();
} else {
    $search = isset($_POST['search']) ? $_POST['search'] : '';
    $sql = "SELECT * FROM tblbooks WHERE BookName LIKE :search";
    $query = $dbh->prepare($sql);
    $query->bindValue(':search', '%' . $search . '%', PDO::PARAM_STR);
    $query->execute();
    $books = $query->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>Available Books</title>
    <!-- Bootstrap CSS -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- Font Awesome CSS -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- Custom CSS -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- Google Font -->
    <link href='http://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
</head>

<body>
    <!-- Header -->
    <?php include('includes/header.php'); ?>
    <!-- End Header -->

    <div class="content-wrapper">
        <div class="container">
            <!-- Search Bar -->
            <div class="row">
                <div class="col-md-12">
                    <form method="post">
                        <div class="input-group">
                            <input type="text" class="form-control" placeholder="Search Books by Name" name="search" value="<?php echo $search; ?>">
                            <div class="input-group-btn">
                                <button class="btn btn-default" type="submit">
                                    <i class="glyphicon glyphicon-search"></i>
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <!-- End Search Bar -->

    <!-- Content Wrapper -->
    <div class="content-wrapper">
        <div class="container">
            <!-- Available Books Section -->
            <div class="row">
                <div class="col-md-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Available Books</h3>
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Book Name</th>
                                            <th>Category</th>
                                            <th>Author</th>
                                            <th>ISBN Number</th>
                                            <th>Price</th>
                                            <th>Count</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($books as $book) { ?>
                                            <tr>
                                                <td><?php echo $book['id']; ?></td>
                                                <td><?php echo $book['BookName']; ?></td>
                                                <td><?php echo $book['CatId']; ?></td>
                                                <td><?php echo $book['Author']; ?></td>
                                                <td><?php echo $book['ISBNNumber']; ?></td>
                                                <td><?php echo $book['BookPrice']; ?></td>
                                                <td><?php echo $book['Count']; ?></td>
                                            </tr>
                                        <?php } ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- End Available Books Section -->
        </div>
    </div>

    <!-- Footer -->
    <?php include('includes/footer.php'); ?>
    <!-- End Footer -->

    <!-- Bootstrap JS -->
    <script src="assets/js/jquery-1.10.2.js"></script>
    <script src="assets/js/bootstrap.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/custom.js"></script>
</body>

</html>
<?php
}
?>
