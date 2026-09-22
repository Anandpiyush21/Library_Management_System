<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();

$rid   = (int) ($_GET['rid'] ?? 0);
$error = '';

if (isset($_POST['return'])) {
    lms_csrf_verify();
    // The fine is computed from the loan policy; the librarian may override it
    // (waiver, damaged copy, disputed date) but never has to calculate it.
    $fine = isset($_POST['fine']) && $_POST['fine'] !== '' ? (float) $_POST['fine'] : null;

    if (lms_return_book($dbh, $rid, $fine)) {
        lms_flash_set('msg', 'Book returned successfully.');
        header('location:manage-issued-books.php');
        exit();
    }
    $error = 'This loan has already been closed.';
}

$sql = "SELECT s.FullName, s.StudentId, b.BookName, b.ISBNNumber,
               i.IssuesDate, i.ReturnDate, i.id AS rid, i.fine, i.RetrunStatus
        FROM tblissuedbookdetails i
        JOIN tblstudents s ON s.StudentId = i.StudentID
        JOIN tblbooks b ON b.id = i.BookId
        WHERE i.id = :rid";
$query = $dbh->prepare($sql);
$query->execute([':rid' => $rid]);
$loan = $query->fetch();

if (!$loan) {
    lms_flash_set('error', 'No such issue record.');
    header('location:manage-issued-books.php');
    exit();
}

$daysOverdue  = lms_days_overdue($loan->IssuesDate);
$suggestedFine = lms_calculate_fine($loan->IssuesDate);
?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Issued Book Details</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- FONT AWESOME STYLE  -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- CUSTOM STYLE  -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- GOOGLE FONT -->
    <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
<script>
// function for get student name
function getstudent() {
$("#loaderIcon").show();
jQuery.ajax({
url: "get_student.php",
data:'studentid='+$("#studentid").val(),
type: "POST",
success:function(data){
$("#get_student_name").html(data);
$("#loaderIcon").hide();
},
error:function (){}
});
}

//function for book details
function getbook() {
$("#loaderIcon").show();
jQuery.ajax({
url: "get_book.php",
data:'bookid='+$("#bookid").val(),
type: "POST",
success:function(data){
$("#get_book_name").html(data);
$("#loaderIcon").hide();
},
error:function (){}
});
}

</script> 
<style type="text/css">
  .others{
    color:red;
}

</style>


</head>
<body>
      <!------MENU SECTION START-->
<?php include('includes/header.php');?>
<!-- MENU SECTION END-->
    <div class="content-wrapper">
         <div class="container">
        <div class="row pad-botm">
            <div class="col-md-12">
                <h4 class="header-line">Issued Book Details</h4>
                
                            </div>

</div>
<div class="row">
<div class="col-md-10 col-sm-6 col-xs-12 col-md-offset-1">
<div class="panel panel-info">
<div class="panel-heading">
Issued Book Details
</div>
<div class="panel-body">
<form role="form" method="post">
<?php echo lms_csrf_field(); ?>
<?php if ($error !== '') { ?>
<div class="alert alert-danger"><?php echo e($error); ?></div>
<?php } ?>

<div class="form-group">
<label>Member :</label>
<?php echo e($loan->FullName); ?> (<?php echo e($loan->StudentId); ?>)
</div>

<div class="form-group">
<label>Book Name :</label>
<?php echo e($loan->BookName); ?>
</div>

<div class="form-group">
<label>ISBN :</label>
<?php echo e($loan->ISBNNumber); ?>
</div>

<div class="form-group">
<label>Book Issued Date :</label>
<?php echo e($loan->IssuesDate); ?>
</div>

<div class="form-group">
<label>Due Date :</label>
<?php echo e(lms_due_date($loan->IssuesDate)->format('d M Y')); ?>
<?php if ($daysOverdue > 0 && (int) $loan->RetrunStatus === 0) { ?>
    <span style="color:red">(overdue by <?php echo e($daysOverdue); ?> day(s))</span>
<?php } ?>
</div>

<div class="form-group">
<label>Book Returned Date :</label>
<?php echo (int) $loan->RetrunStatus === 1 ? e($loan->ReturnDate) : 'Not returned yet'; ?>
</div>

<div class="form-group">
<label>Fine (in INR) :</label>
<?php if ((int) $loan->RetrunStatus === 0) { ?>
    <input class="form-control" type="number" step="0.01" min="0" name="fine" id="fine"
           value="<?php echo e(number_format($suggestedFine, 2, '.', '')); ?>" required />
    <span class="help-block">
        Calculated as <?php echo e($daysOverdue); ?> overdue day(s) &times;
        INR <?php echo e(number_format(FINE_PER_DAY, 2)); ?>. Edit to waive or adjust.
    </span>
<?php } else { ?>
    <?php echo e(number_format((float) $loan->fine, 2)); ?>
<?php } ?>
</div>

<?php if ((int) $loan->RetrunStatus === 0) { ?>
<button type="submit" name="return" id="submit" class="btn btn-info">Return Book</button>
<?php } ?>

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
