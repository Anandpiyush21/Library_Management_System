<?php
require_once __DIR__ . '/includes/config.php';
lms_require_admin();
if (isset($_POST['delete'])) {
    lms_csrf_verify();
    $id = (int) $_POST['id'];

    $inUse = $dbh->prepare("SELECT COUNT(*) FROM tblbooks WHERE AuthorId = :id");
    $inUse->execute([':id' => $id]);

    if ($inUse->fetchColumn() > 0) {
        lms_flash_set('error', 'This author is still referenced by one or more books.');
    } else {
        $dbh->prepare("DELETE FROM tblauthors WHERE id = :id")->execute([':id' => $id]);
        lms_flash_set('delmsg', 'Author deleted successfully.');
    }
    header('location:manage-authors.php');
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
    <title>IIIT Raichur | Manage Authors</title>
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
                <h4 class="header-line">Manage Authors</h4>
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
                           Authors Listing
                        </div>
                        <div class="panel-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-bordered table-hover" id="dataTables-example">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Author</th>
                                         
                                            <th>Creation Date</th>
                                            <th>Updation Date</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
<?php $sql = "SELECT * from  tblauthors";
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
                                            <td class="center"><?php echo e($result->AuthorName);?></td>
                                            <td class="center"><?php echo e($result->creationDate);?></td>
                                            <td class="center"><?php echo e($result->UpdationDate);?></td>
                                            <td class="center">

                                            <a href="edit-author.php?athrid=<?php echo e($result->id);?>"><button class="btn btn-primary"><i class="fa fa-edit "></i> Edit</button> 
                                          <form method="post" style="display:inline" onsubmit="return confirm('Are you sure you want to delete?');">
<?php echo lms_csrf_field(); ?>
<input type="hidden" name="id" value="<?php echo e($result->id); ?>" />
<button type="submit" name="delete" class="btn btn-danger"><i class="fa fa-trash"></i> Delete</button>
</form></td>
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
