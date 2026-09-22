<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();
    ?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>IIIT Raichur | Manage Issued Books</title>
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
                <h4 class="header-line">Manage Issued Books</h4>
    </div>
     <div class="row">
    <?php echo lms_flash_render(); ?>
</div>


        </div>
            <div class="row">
                <div class="col-md-12">
                    <!-- Advanced Tables -->
                    <div class="panel panel-default">
                        <div class="panel-heading">
                          Issued Books
                          &nbsp;|&nbsp;
                          <a href="?filter=all">All</a> &middot;
                          <a href="?filter=open">On loan</a> &middot;
                          <a href="?filter=overdue">Overdue</a>
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover" id="dataTables-example">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Student Name</th>
                                            <th>Book Name</th>
                                            <th>ISBN </th>
                                            <th>Issued Date</th>
                                            <th>Due Date</th>
                                            <th>Status</th>
                                            <th>Fine (INR)</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
<?php
$filter = $_GET['filter'] ?? 'all';   // all | open | overdue
$sql = "SELECT s.FullName, s.StudentId, b.BookName, b.ISBNNumber,
               i.IssuesDate, i.ReturnDate, i.RetrunStatus, i.fine, i.id AS rid
        FROM tblissuedbookdetails i
        JOIN tblstudents s ON s.StudentId = i.StudentID
        JOIN tblbooks b ON b.id = i.BookId
        ORDER BY i.id DESC";
$query = $dbh->prepare($sql);
$query->execute();
$cnt = 1;
foreach ($query->fetchAll() as $result) {
    $returned = (int) $result->RetrunStatus === 1;
    $days     = $returned ? 0 : lms_days_overdue($result->IssuesDate);
    if ($filter === 'open' && $returned) { continue; }
    if ($filter === 'overdue' && ($returned || $days === 0)) { continue; }
?>
                                        <tr class="odd gradeX">
                                            <td class="center"><?php echo e($cnt); ?></td>
                                            <td class="center"><?php echo e($result->FullName); ?> (<?php echo e($result->StudentId); ?>)</td>
                                            <td class="center"><?php echo e($result->BookName); ?></td>
                                            <td class="center"><?php echo e($result->ISBNNumber); ?></td>
                                            <td class="center"><?php echo e($result->IssuesDate); ?></td>
                                            <td class="center"><?php echo e(lms_due_date($result->IssuesDate)->format('d M Y')); ?></td>
                                            <td class="center">
                                            <?php if ($returned) { ?>
                                                Returned on <?php echo e($result->ReturnDate); ?>
                                            <?php } elseif ($days > 0) { ?>
                                                <span style="color:red">Overdue by <?php echo e($days); ?> day(s)</span>
                                            <?php } else { ?>
                                                <span style="color:#3c763d">On loan</span>
                                            <?php } ?>
                                            </td>
                                            <td class="center">
                                                <?php echo e(number_format($returned ? (float) $result->fine : lms_calculate_fine($result->IssuesDate), 2)); ?>
                                            </td>
                                            <td class="center">
                                                <a href="update-issue-bookdeails.php?rid=<?php echo e($result->rid); ?>" class="btn btn-primary">
                                                    <i class="fa fa-edit"></i> <?php echo $returned ? 'View' : 'Return'; ?>
                                                </a>
                                            </td>
                                        </tr>
<?php $cnt++; } ?>                                      
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
