<?php
require_once __DIR__ . '/includes/config.php';
$studentId = lms_require_student();

$error = '';
$msg   = '';

if (isset($_POST['update'])) {
    lms_csrf_verify();
    $fname    = trim($_POST['fullanme'] ?? '');
    $mobileno = trim($_POST['mobileno'] ?? '');

    if ($fname === '') {
        $error = 'Your name cannot be empty.';
    } elseif (!preg_match('/^[0-9]{10}$/', $mobileno)) {
        $error = 'Mobile number must be exactly 10 digits.';
    } else {
        $sql = "UPDATE tblstudents SET FullName = :fname, MobileNumber = :mobileno
                WHERE StudentId = :sid";
        $dbh->prepare($sql)->execute([
            ':fname' => $fname, ':mobileno' => $mobileno, ':sid' => $studentId,
        ]);
        $msg = 'Your profile has been updated.';
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
    <!--[if IE]>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <![endif]-->
    <title>IIIT Raichur | My Profile</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />

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
                <h4 class="header-line">My Profile</h4>
                
                            </div>

        </div>
             <div class="row">
           
<div class="col-md-9 col-md-offset-1">
               <div class="panel panel-danger">
                        <div class="panel-heading">
                           My Profile
                        </div>
                        <div class="panel-body">
                            <form name="signup" method="post">
                                <?php echo lms_csrf_field(); ?>
                                <?php if ($error !== '') { ?>
                                    <div class="alert alert-danger"><?php echo e($error); ?></div>
                                <?php } elseif ($msg !== '') { ?>
                                    <div class="alert alert-success"><?php echo e($msg); ?></div>
                                <?php } ?>
<?php 
$sid = $studentId;
$sql="SELECT StudentId,FullName,EmailId,MobileNumber,RegDate,UpdationDate,Status,fines from  tblstudents  where StudentId=:sid ";
$query = $dbh -> prepare($sql);
$query-> bindParam(':sid', $sid, PDO::PARAM_STR);
$query->execute();
$results=$query->fetchAll(PDO::FETCH_OBJ);
$cnt=1;
if($query->rowCount() > 0)
{
foreach($results as $result)
{               ?>  

<div class="form-group">
<label>Student ID : </label>
<?php echo e($result->StudentId);?>
</div>

<div class="form-group">
<label>Reg Date : </label>
<?php echo e($result->RegDate);?>
</div>
<?php if($result->UpdationDate!=""){?>
<div class="form-group">
<label>Last Updation Date : </label>
<?php echo e($result->UpdationDate);?>
</div>
<?php } ?>


<div class="form-group">
<label>Outstanding Fine (INR) : </label>
<?php echo e(number_format((float) $result->fines, 2)); ?>
</div>

<div class="form-group">
<label>Profile Status : </label>
<?php if($result->Status==1){?>
<span style="color: green">Active</span>
<?php } else { ?>
<span style="color: red">Blocked</span>
<?php }?>
</div>


<div class="form-group">
<label>Enter Full Name</label>
<input class="form-control" type="text" name="fullanme" value="<?php echo e($result->FullName);?>" autocomplete="off" required />
</div>


<div class="form-group">
<label>Mobile Number :</label>
<input class="form-control" type="text" name="mobileno" maxlength="10" pattern="[0-9]{10}" value="<?php echo e($result->MobileNumber);?>" autocomplete="off" required />
</div>
                                        
<div class="form-group">
<label>Enter Email</label>
<input class="form-control" type="email" name="email" id="emailid" value="<?php echo e($result->EmailId);?>"  autocomplete="off" required readonly />
</div>
<?php }} ?>
                              
<button type="submit" name="update" class="btn btn-primary" id="submit">Update Now </button>

                                    </form>
                            </div>
                        </div>
                            </div>
        </div>
    </div>
    </div>
     <!-- CONTENT-WRAPPER SECTION END-->
    <?php include('includes/footer.php');?>
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
      <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
</body>
</html>
