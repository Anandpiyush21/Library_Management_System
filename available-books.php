<?php
require_once __DIR__ . '/includes/config.php';
$studentId = lms_require_student();

$search = trim($_GET['search'] ?? '');

// Catalogue search across title, author and ISBN, with the live copy count
// so members can see what is actually on the shelf before walking over.
$sql = "SELECT b.id, b.BookName, b.Author, b.ISBNNumber, b.BookPrice, b.Count,
               COALESCE(c.CategoryName, 'Uncategorised') AS CategoryName
        FROM tblbooks b
        LEFT JOIN tblcategory c ON c.id = b.CatId
        WHERE b.BookName LIKE :q1 OR b.Author LIKE :q2 OR b.ISBNNumber LIKE :q3
        ORDER BY b.BookName";
$query = $dbh->prepare($sql);
$like = '%' . $search . '%';
$query->execute([':q1' => $like, ':q2' => $like, ':q3' => $like]);
$books = $query->fetchAll();
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Catalogue</title>
    <!-- Bootstrap CSS -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- Font Awesome CSS -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- Custom CSS -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- Google Font -->
    <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
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
                    <form method="get">
                        <div class="input-group">
                            <input type="text" class="form-control" placeholder="Search by title, author or ISBN" name="search" value="<?php echo e($search); ?>">
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
                                            <th>Availability</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($books as $book) { $available = (int) $book->Count > 0; ?>
                                            <tr>
                                                <td><?php echo e($book->id); ?></td>
                                                <td><?php echo e($book->BookName); ?></td>
                                                <td><?php echo e($book->CategoryName); ?></td>
                                                <td><?php echo e($book->Author); ?></td>
                                                <td><?php echo e($book->ISBNNumber); ?></td>
                                                <td><?php echo e(number_format((float) $book->BookPrice, 2)); ?></td>
                                                <td>
                                                    <?php if ($available) { ?>
                                                        <span style="color:#3c763d"><?php echo e($book->Count); ?> available</span>
                                                    <?php } else { ?>
                                                        <span style="color:red">All copies on loan</span>
                                                    <?php } ?>
                                                </td>
                                            </tr>
                                        <?php } ?>
                                        <?php if (!$books) { ?>
                                            <tr><td colspan="7" class="text-center">No book matches &ldquo;<?php echo e($search); ?>&rdquo;.</td></tr>
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
