<?php
require_once __DIR__ . '/includes/config.php';
lms_session_start();

$error = '';

if (isset($_POST['login'])) {
    lms_csrf_verify();
    $email    = trim($_POST['emailid'] ?? '');
    $password = $_POST['password'] ?? '';

    $sql = "SELECT StudentId, EmailId, Password, Status FROM tblstudents WHERE EmailId = :email";
    $query = $dbh->prepare($sql);
    $query->bindParam(':email', $email, PDO::PARAM_STR);
    $query->execute();
    $student = $query->fetch();

    if ($student && lms_verify_password($password, $student->Password)) {
        if ((int) $student->Status !== 1) {
            $error = 'Your account has been blocked. Please contact the librarian.';
        } else {
            if (lms_password_needs_rehash($student->Password)) {
                lms_upgrade_password($dbh, 'tblstudents', 'EmailId', $student->EmailId, $password);
            }
            session_regenerate_id(true);           // defeat session fixation
            $_SESSION['login'] = $student->EmailId;
            $_SESSION['stdid'] = $student->StudentId;
            header('location:dashboard.php');
            exit();
        }
    } else {
        // One message for both cases, so the form cannot be used to
        // enumerate which e-mail addresses are registered.
        $error = 'Invalid e-mail address or password.';
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
    <title>IIIT Raichur | Member Login</title>
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
<div class="content-wrapper">
<div class="container">
<div class="row pad-botm">
<div class="col-md-12">
<h4 class="header-line">Member Login</h4>
</div>
</div>
             
<!--LOGIN PANEL START-->           
<div class="row">
<div class="col-md-6 col-sm-6 col-xs-12 col-md-offset-3" >
<div class="panel panel-info">
<div class="panel-heading">
 LOGIN FORM
</div>
<div class="panel-body">
<form role="form" method="post">
<?php echo lms_csrf_field(); ?>
<?php if ($error !== '') { ?>
<div class="alert alert-danger"><?php echo e($error); ?></div>
<?php } ?>

<div class="form-group">
<label>Enter Email id</label>
<input class="form-control" type="text" name="emailid" required autocomplete="off" />
</div>
<div class="form-group">
<label>Password</label>
<input class="form-control" type="password" name="password" required autocomplete="off"  />
<p class="help-block">Forgotten your password? Ask the librarian to reset it.</p>
</div>


 <button type="submit" name="login" class="btn btn-info">LOGIN </button> | <a href="signup.php">Not registered yet?</a>
</form>
 </div>
</div>
</div>
</div>  
<!---LOGIN PABNEL END-->            
             
 
    </div>
    </div>
     <!-- CONTENT-WRAPPER SECTION END-->
 <?php include('includes/footer.php');?>
      <!-- FOOTER SECTION END-->
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
      <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>

</body>
</html>
