<?php include "_header.php"; ?>

          <div id="content">
            <!--start site map code-->
            <h1>Site Map</h1>
            <ul>
              <?php
	$files = glob("*.php");
	$ignore_files = array( //add any file names of files you don't want to appear in the site map
		"_header.php",
		"_footer.php",
		"_weather.php",
		"_current_weather.php",
		"formsubmit.php",
		"formsubmit_error.php",
		"formsubmit_newsletter.php",
		"search.php",
		"maillist.php",
		"links.php",
	);
	foreach($files as $f){ 
		if(in_array($f,$ignore_files))continue;
		$file_data = file_get_contents($f);
		if(preg_match('/<title>([^<]+)<\/title>/i',$file_data,$matches)){
		$page_title = $matches[1];
		}else{
		$page_title = $f;
		}
		
		?>
              <li><a href="<?=$f;?>">
                <?=$page_title;?>
                </a></li>
              <?
	}
	?>
            </ul>
            <!--end site map code-->

<?php include "_footer.php"; ?>
