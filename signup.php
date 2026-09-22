<?php
require_once __DIR__ . '/includes/config.php';
lms_session_start();

$error = '';
$msg   = '';

if (isset($_POST['signup'])) {
    lms_csrf_verify();
    $fname    = trim($_POST['fullanme'] ?? '');
    $mobileno = trim($_POST['mobileno'] ?? '');
    $email    = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Please enter a valid e-mail address.';
    } elseif (!preg_match('/^[0-9]{10}$/', $mobileno)) {
        $error = 'Mobile number must be exactly 10 digits.';
    } elseif (strlen($password) < 8) {
        $error = 'Password must be at least 8 characters long.';
    } elseif ($password !== ($_POST['confirmpassword'] ?? '')) {
        $error = 'Password and confirmation do not match.';
    } else {
        try {
            $StudentId = lms_next_student_id(__DIR__ . '/studentid.txt');
            $sql = "INSERT INTO tblstudents (StudentId, FullName, MobileNumber, EmailId, Password, Status)
                    VALUES (:StudentId, :fname, :mobileno, :email, :password, 1)";
            $query = $dbh->prepare($sql);
            $query->execute([
                ':StudentId' => $StudentId,
                ':fname'     => $fname,
                ':mobileno'  => $mobileno,
                ':email'     => $email,
                ':password'  => lms_hash_password($password),
            ]);
            $msg = 'Registration successful. Your library card number is ' . $StudentId
                 . ' — please note it down, you will need it when borrowing books.';
        } catch (PDOException $e) {
            // 23000 = integrity constraint: the e-mail is already registered.
            $error = $e->getCode() === '23000'
                ? 'That e-mail address is already registered.'
                : 'Something went wrong. Please try again.';
            error_log('Signup failed: ' . $e->getMessage());
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
    <!--[if IE]>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <![endif]-->
    <title>IIIT Raichur | Student Signup</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- FONT AWESOME STYLE  -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- CUSTOM STYLE  -->
    <link href="assets/css/style.css" rel="stylesheet" />
    <!-- GOOGLE FONT -->
    <link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
    <script type="text/javascript">
        function valid() {
            if (document.signup.password.value != document.signup.confirmpassword.value) {
                alert("Password and Confirm Password Field do not match  !!");
                document.signup.confirmpassword.focus();
                return false;
            }
            return true;
        }
    </script>
    <script>
        function checkAvailability() {
            $("#loaderIcon").show();
            jQuery.ajax({
                url: "check_availability.php",
                data: 'emailid=' + $("#emailid").val(),
                type: "POST",
                success: function (data) {
                    $("#user-availability-status").html(data);
                    $("#loaderIcon").hide();
                },
                error: function () { }
            });
        }
    </script>

</head>

<body>
    <!------MENU SECTION START-->
    <?php include('includes/header.php'); ?>
    <!-- MENU SECTION END-->
    <div class="content-wrapper">
        <div class="container">
            <div class="row pad-botm">
                <div class="col-md-12">
                    <h4 class="header-line">Member Signup</h4>

                </div>

            </div>
            <div class="row">

                <div class="col-md-9 col-md-offset-1">
                    <div class="panel panel-danger">
                        <div class="panel-heading">
                            Signup Form
                        </div>
                        <div class="panel-body">
                            <form name="signup" method="post" onSubmit="return valid();">
                                <?php echo lms_csrf_field(); ?>
                                <?php if ($error !== '') { ?>
                                    <div class="alert alert-danger"><?php echo e($error); ?></div>
                                <?php } elseif ($msg !== '') { ?>
                                    <div class="alert alert-success"><?php echo e($msg); ?></div>
                                <?php } ?>
                                <div class="form-group">
                                    <label>Enter Full Name</label>
                                    <input class="form-control" type="text" name="fullanme" autocomplete="off"
                                        required />
                                </div>


                                <div class="form-group">
                                    <label>Mobile Number :</label>
                                    <input class="form-control" type="text" name="mobileno" maxlength="10" pattern="[0-9]{10}"
                                        autocomplete="off" required />
                                </div>

                                <div class="form-group">
                                    <label>Enter Email</label>
                                    <input class="form-control" type="email" name="email" id="emailid"
                                        onBlur="checkAvailability()" autocomplete="off" required />
                                    <span id="user-availability-status" style="font-size:12px;"></span>
                                </div>

                                <div class="form-group">
                                    <label>Enter Password</label>
                                    <input class="form-control" type="password" name="password" minlength="8" autocomplete="off"
                                        required />
                                    <span class="help-block">Minimum 8 characters.</span>
                                </div>

                                <div class="form-group">
                                    <label>Confirm Password </label>
                                    <input class="form-control" type="password" name="confirmpassword"
                                        autocomplete="off" required />
                                </div>
                                <div class="form-group">
                                    <button type="submit" name="signup" class="btn btn-danger" id="submit">Register Now
                                    </button>

                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- CONTENT-WRAPPER SECTION END-->
    <?php include('includes/footer.php'); ?>
    <script src="assets/js/jquery-1.10.2.js"></script>
    <!-- BOOTSTRAP SCRIPTS  -->
    <script src="assets/js/bootstrap.js"></script>
    <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
</body>

</html>