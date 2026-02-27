<?php

header('Content-Type: text/html;charset=UTF-8');
   
    if(isset($_POST['plfs'])){   
        $finam=$_FILES['img_file']['name'];
        $finam = str_replace(" ", "_", $finam);
        $dirfi="FarSto/" . $finam;
        move_uploaded_file ($_FILES['img_file']['tmp_name'], $dirfi);  
      
        echo "<body onload=\"parent.Sho_pic('" . $finam . "')\"></body>";
}
?>