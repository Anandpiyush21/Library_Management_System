<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

$error = '';

if (isset($_POST['add'])) {
    lms_csrf_verify();
    $bookname = trim($_POST['bookname'] ?? '');
    $category = (int) ($_POST['category'] ?? 0);
    $author   = trim($_POST['author'] ?? '');
    $isbn     = trim($_POST['isbn'] ?? '');
    $price    = (float) ($_POST['price'] ?? 0);
    $count    = max(0, (int) ($_POST['count'] ?? 0));

    if ($bookname === '' || $author === '') {
        $error = 'Title and author are required.';
    } elseif (!preg_match('/^[0-9Xx-]{10,17}$/', $isbn)) {
        $error = 'Please enter a valid 10- or 13-digit ISBN.';
    } else {
        try {
            // Keep the free-text author in step with the normalised author
            // table, so the Edit Book join always has a row to work with.
            $lookup = $dbh->prepare('SELECT id FROM tblauthors WHERE AuthorName = :name');
            $lookup->execute([':name' => $author]);
            $authorId = $lookup->fetchColumn();
            if (!$authorId) {
                $dbh->prepare('INSERT INTO tblauthors (AuthorName) VALUES (:name)')
                    ->execute([':name' => $author]);
                $authorId = $dbh->lastInsertId();
            }

            $sql = "INSERT INTO tblbooks (BookName, CatId, AuthorId, Author, ISBNNumber, BookPrice, Count)
                    VALUES (:bookname, :category, :authorid, :author, :isbn, :price, :count)";
            $dbh->prepare($sql)->execute([
                ':bookname' => $bookname,
                ':category' => $category,
                ':authorid' => $authorId,
                ':author'   => $author,
                ':isbn'     => $isbn,
                ':price'    => $price,
                ':count'    => $count,
            ]);
            lms_flash_set('msg', 'Book added to the catalogue.');
            header('location:manage-books.php');
            exit();
        } catch (PDOException $e) {
            $error = $e->getCode() === '23000'
                ? 'A book with that ISBN is already in the catalogue.'
                : 'Something went wrong. Please try again.';
            error_log('Add book failed: ' . $e->getMessage());
        }
    }
}
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Add Book</title>
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
    <?php include('includes/header.php'); ?>
    <div class="content-wrapper">
        <div class="container">
            <div class="row pad-botm">
                <div class="col-md-12">
                    <h4 class="header-line">Add Book</h4>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 col-sm-6 col-xs-12 col-md-offset-3">
                    <div class="panel panel-info">
                        <div class="panel-heading">Book Info</div>
                        <div class="panel-body">
                            <form role="form" method="post">
                                <?php echo lms_csrf_field(); ?>
                                <?php if ($error !== '') { ?>
                                    <div class="alert alert-danger"><?php echo e($error); ?></div>
                                <?php } ?>
                                <div class="form-group">
                                    <label>Book Name<span style="color:red;">*</span></label>
                                    <input class="form-control" type="text" name="bookname" autocomplete="off" required />
                                </div>
                                <div class="form-group">
                                    <label>Category<span style="color:red;">*</span></label>
                                    <select class="form-control" name="category" required="required">
                                        <option value="">Select Category</option>
                                        <!-- Fetch and display categories from the database -->
                                        <?php 
                                            $status = 1;
                                            $sql = "SELECT * from tblcategory where Status=:status";
                                            $query = $dbh->prepare($sql);
                                            $query->bindParam(':status', $status, PDO::PARAM_STR);
                                            $query->execute();
                                            $results = $query->fetchAll(PDO::FETCH_OBJ);
                                            if($query->rowCount() > 0) {
                                                foreach($results as $result) {
                                        ?>
                                        <option value="<?php echo e($result->id); ?>"><?php echo e($result->CategoryName); ?></option>
                                        <?php }} ?> 
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Author<span style="color:red;">*</span></label>
                                    <input class="form-control" type="text" name="author" autocomplete="off" required />
                                </div>
                                <div class="form-group">
                                    <label>ISBN Number<span style="color:red;">*</span></label>
                                    <input class="form-control" type="text" name="isbn" required="required" autocomplete="off" />
                                    <p class="help-block">An ISBN is an International Standard Book Number.ISBN Must be unique</p>
                                </div>
                                <div class="form-group">
                                    <label>Price<span style="color:red;">*</span></label>
                                    <input class="form-control" type="text" name="price" autocomplete="off" required="required" />
                                </div>
                                <div class="form-group">
                                <label>Count<span style="color:red;">*</span></label>
                                <input class="form-control" type="number" name="count" autocomplete="off" required="required" />
                                </div>

                                <button type="submit" name="add" class="btn btn-info">Add</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <?php include('includes/footer.php'); ?>
    <script src="assets/js/jquery-1.10.2.js"></script>
    <script src="assets/js/bootstrap.js"></script>
    <script src="assets/js/custom.js"></script>
</body>
</html>
