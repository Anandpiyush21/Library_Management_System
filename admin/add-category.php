<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

$error = '';

if (isset($_POST['create'])) {
    lms_csrf_verify();
    $category = trim($_POST['category'] ?? '');
    $status   = (int) ($_POST['status'] ?? 1) === 1 ? 1 : 0;

    if ($category === '') {
        $error = 'Please enter a category name.';
    } else {
        try {
            $dbh->prepare('INSERT INTO tblcategory (CategoryName, Status) VALUES (:category, :status)')
                ->execute([':category' => $category, ':status' => $status]);
            lms_flash_set('msg', 'Category created successfully.');
            header('location:manage-categories.php');
            exit();
        } catch (PDOException $e) {
            $error = $e->getCode() === '23000'
                ? 'That category already exists.'
                : 'Something went wrong. Please try again.';
            error_log('Add category failed: ' . $e->getMessage());
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
    <title>IIIT Raichur | Add Categories</title>
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
<?php include('includes/header.php');?>
<!-- MENU SECTION END-->
    <div class="content-wra
    <div class="content-wrapper">
         <div class="container">
        <div class="row pad-botm">
            <div class="col-md-12">
                <h4 class="header-line">Add category</h4>
                
                            </div>

</div>
<div class="row">
<div class="col-md-6 col-sm-6 col-xs-12 col-md-offset-3">
<div class="panel panel-info">
<div class="panel-heading">
Category Info
</div>
<div class="panel-body">
<form role="form" method="post">
<?php echo lms_csrf_field(); ?>
<?php if ($error !== '') { ?>
<div class="alert alert-danger"><?php echo e($error); ?></div>
<?php } ?>
<div class="form-group">
<label>Category Name</label>
<input class="form-control" type="text" name="category" autocomplete="off" required />
</div>
<div class="form-group">
<label>Status</label>
 <div class="radio">
<label>
<input type="radio" name="status" id="status" value="1" checked="checked">Active
</label>
</div>
<div class="radio">
<label>
<input type="radio" name="status" id="status" value="0">Inactive
</label>
</div>

</div>
<button type="submit" name="create" class="btn btn-info">Create </button>

                                    </form>
                            </div>
                        </div>
                            </div>

        </div>
   
    </div>
    </div>
     <!-- CONTENT-WRAPPER SECTION END-->
  <?php include('includes/footer.php');?>
      <!-- FOOTER SECTION END-->
    <!-- JAVASCRIPT FILES PLACED AT THE BOTTOM TO REDUCE THE LOADING TIME  -->
    <!-- CORE JQUERY  -->
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
      <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
</body>
</html>
