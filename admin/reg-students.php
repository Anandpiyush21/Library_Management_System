<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();
// Blocking or re-activating a member changes state, so it is a CSRF-checked
// POST rather than a link that any crawler could follow.
if (isset($_POST['setstatus'])) {
    lms_csrf_verify();
    $id     = (int) $_POST['id'];
    $status = (int) $_POST['status'] === 1 ? 1 : 0;

    $dbh->prepare('UPDATE tblstudents SET Status = :status WHERE id = :id')
        ->execute([':status' => $status, ':id' => $id]);

    lms_flash_set('msg', $status === 1 ? 'Member re-activated.' : 'Member blocked.');
    header('location:reg-students.php');
exit();
    exit();
}

    ?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Manage Reg Students</title>
    <!-- BOOTSTRAP CORE STYLE  -->
    <link href="assets/css/bootstrap.css" rel="stylesheet" />
    <!-- FONT AWESOME STYLE  -->
    <link href="assets/css/font-awesome.css" rel="stylesheet" />
    <!-- DATATABLE STYLE  -->
    <link href="assets/js/dataTables/dataTables.bootstrap.css" rel="stylesheet" />
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
                <h4 class="header-line">Manage Reg Students</h4>
    </div>


        </div>
<div class="row"><?php echo lms_flash_render(); ?></div>
            <div class="row">
                <div class="col-md-12">
                    <!-- Advanced Tables -->
                    <div class="panel panel-default">
                        <div class="panel-heading">
                          Reg Students
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover" id="dataTables-example">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Student ID</th>
                                            <th>Student Name</th>
                                            <th>Email id </th>
                                            <th>Mobile Number</th>
                                            <th>Reg Date</th>
                                            <th>Fine</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
<?php $sql = "SELECT * from tblstudents ORDER BY id DESC";
$query = $dbh -> prepare($sql);
$query->execute();
$results=$query->fetchAll(PDO::FETCH_OBJ);
$cnt=1;
if($query->rowCount() > 0)
{
foreach($results as $result)
{               ?>                                      
                                        <tr class="odd gradeX">
                                            <td class="center"><?php echo e($cnt);?></td>
                                            <td class="center"><?php echo e($result->StudentId);?></td>
                                            <td class="center"><?php echo e($result->FullName);?></td>
                                            <td class="center"><?php echo e($result->EmailId);?></td>
                                            <td class="center"><?php echo e($result->MobileNumber);?></td>
                                             <td class="center"><?php echo e($result->RegDate);?></td>
                                             <td class="center" style="color: <?php echo $result->fines > 0 ? 'red' : 'green'; ?>;">
                                                <?php echo e($result->fines); ?>
                                            </td>
                                            <td class="center"><?php if($result->Status==1)
                                            {
                                                echo e("Active");
                                            } else {


                                            echo e("Blocked");
}
                                            ?></td>
                                            <td class="center">
<form method="post" style="display:inline"
      onsubmit="return confirm('<?php echo $result->Status == 1 ? 'Block this member?' : 'Re-activate this member?'; ?>');">
    <?php echo lms_csrf_field(); ?>
    <input type="hidden" name="id" value="<?php echo e($result->id); ?>" />
    <input type="hidden" name="status" value="<?php echo $result->Status == 1 ? 0 : 1; ?>" />
    <button type="submit" name="setstatus" class="btn <?php echo $result->Status == 1 ? 'btn-danger' : 'btn-primary'; ?>">
        <?php echo $result->Status == 1 ? 'Block' : 'Activate'; ?>
    </button>
</form>
                                          
                                            </td>
                                        </tr>
 <?php $cnt=$cnt+1;}} ?>                                      
                                    </tbody>
                                </table>
                            </div>
                            
                        </div>
                    </div>
                    <!--End Advanced Tables -->
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
    <!-- DATATABLE SCRIPTS  -->
    <script src="assets/js/dataTables/jquery.dataTables.js"></script>
    <script src="assets/js/dataTables/dataTables.bootstrap.js"></script>
      <!-- CUSTOM SCRIPTS  -->
    <script src="assets/js/custom.js"></script>
</body>
</html>
