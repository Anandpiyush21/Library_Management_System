<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();
// Destructive actions are POST-only and CSRF-checked: a plain <a href=?del=>
// could be triggered by any page the librarian happens to open, and is also
// followed by link pre-fetchers.
if (isset($_POST['delete'])) {
    lms_csrf_verify();
    $id = (int) $_POST['bookid'];

    $onLoan = $dbh->prepare(
        'SELECT COUNT(*) FROM tblissuedbookdetails WHERE BookId = :id AND RetrunStatus = 0'
    );
    $onLoan->execute([':id' => $id]);

    if ($onLoan->fetchColumn() > 0) {
        $_SESSION['error'] = 'This title cannot be removed while copies are still on loan.';
    } else {
        $dbh->prepare('DELETE FROM tblbooks WHERE id = :id')->execute([':id' => $id]);
        $_SESSION['delmsg'] = 'Book deleted successfully.';
    }
    header('location:manage-books.php');
    exit();
}
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Manage Books</title>
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <link href="assets/js/dataTables/dataTables.bootstrap.css" rel="stylesheet" />
    <link href="assets/css/style.css" rel="stylesheet" />
    <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
</head>
<body>
    <?php include('includes/header.php'); ?>
    <div class="content-wrapper">
        <div class="container">
            <div class="row pad-botm">
                <div class="col-md-12">
                    <h4 class="header-line">Manage Books</h4>
                </div>
            </div>
            <div class="row"><?php echo lms_flash_render(); ?></div>
            <div class="row">
                <div class="col-md-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">Books Listing</div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover" id="dataTables-example">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Book Name</th>
                                            <th>Category</th>
                                            <th>Author</th>
                                            <th>ISBN</th>
                                            <th>Price</th>
                                            <th>Copies on shelf</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php 
                                        $sql = "SELECT tblbooks.BookName, tblcategory.CategoryName, tblbooks.Author, tblbooks.ISBNNumber, tblbooks.BookPrice,tblbooks.Count, tblbooks.id as bookid FROM tblbooks LEFT JOIN tblcategory ON tblcategory.id=tblbooks.CatId ORDER BY tblbooks.BookName";
                                        $query = $dbh->prepare($sql);
                                        $query->execute();
                                        $results = $query->fetchAll(PDO::FETCH_OBJ);
                                        $cnt = 1;
                                        if($query->rowCount() > 0) {
                                            foreach($results as $result) { ?>                                      
                                                <tr class="odd gradeX">
                                                    <td class="center"><?php echo e($cnt);?></td>
                                                    <td class="center"><?php echo e($result->BookName);?></td>
                                                    <td class="center"><?php echo e($result->CategoryName ?? 'Uncategorised');?></td>
                                                    <td class="center"><?php echo e($result->Author);?></td>
                                                    <td class="center"><?php echo e($result->ISBNNumber);?></td>
                                                    <td class="center"><?php echo e($result->BookPrice);?></td>
                                                    <td class="center"><?php echo e($result->Count);?></td>
                                                    <td class="center">
                                                        <a href="edit-book.php?bookid=<?php echo e($result->bookid); ?>" class="btn btn-primary">
                                                            <i class="fa fa-edit"></i> Edit
                                                        </a>
                                                        <form method="post" style="display:inline"
                                                              onsubmit="return confirm('Delete this book from the catalogue?');">
                                                            <?php echo lms_csrf_field(); ?>
                                                            <input type="hidden" name="bookid" value="<?php echo e($result->bookid); ?>" />
                                                            <button type="submit" name="delete" class="btn btn-danger">
                                                                <i class="fa fa-trash"></i> Delete
                                                            </button>
                                                        </form>
                                                    </td>
                                                </tr>
                                                <?php $cnt = $cnt + 1;
                                            }
                                        } ?>                                      
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="assets/js/jquery-1.10.2.js"></script>
    <script src="assets/js/bootstrap.js"></script>
    <script src="assets/js/dataTables/jquery.dataTables.js"></script>
    <script src="assets/js/dataTables/dataTables.bootstrap.js"></script>
    <script src="assets/js/custom.js"></script>
</body>
</html>
