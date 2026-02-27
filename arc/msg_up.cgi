#!/usr/bin/perl
use lib '/Users/archer/perl5/lib/perl5';

use CGI::Carp qw ( fatalsToBrowser );
use CGI qw(:standard);
use POSIX qw(strftime);
use GD;
use Image::GD::Thumbnail;

my $query = new CGI;
my $fmnam = $query->param("nme");
my $mess = $query->param("msg");
my $fpq = $query->param("fapi");
my $boc = $query->param("clr");
my $pic_nam = $query->param("im_nam");
my $cutim = $query->param("tim");

my $size = length($mess);
if($size>4400) { die("Please reduce the size of your message to under 4600 characters") }

$mess=~s/[^\x1f-\x7e\x0a]//g;
$mess =~s/"/\\"/g;
$mess =~s/[><]/*/g;
$mess =~s/\n/<BR>/g;

#********** create thumbnail ************
if($pic_nam) {
   open IN, "FarSto/" . $pic_nam or die "Could not open.";
   my $srcImage = GD::Image->newFromJpeg(*IN);
   close IN;
   my ($thumb) = Image::GD::Thumbnail::create($srcImage,250);
   $thm="FarSto/tn_" . $pic_nam;
   open OUT, ">$thm" or die "Could not save ";
   binmode OUT;
   print OUT $thumb->jpeg;
   close OUT;
}

#********** get latest holen ************
my $holn = 0;
my $line = '';
open (POP, "<epa.js");
while ($line = <POP>) { if (substr($line, 0, 5) eq 'hopo[') { $holn++ }}
close POP;

#********** log message. ************
open (POP,">>epa.js");
if($pic_nam) {
   print POP "\n\nhopo[$holn]=\"$boc'><TD Style='text-align:left'>$fpq<A href=javascript:Img_up('FarSto/$pic_nam')><img src='$thm' height=\" + brwi + \" style='float:right'></A><font color='navy'>From: &nbsp; <B>$fmnam</B>\" + spcs + \"$cutim</font><BR><BR>$mess\";";
} else {
   print POP "\n\nhopo[$holn]=\"$boc'><TD Style='text-align:left'>$fpq<font color='navy'>From: &nbsp; <B>$fmnam</B>\" + spcs + \"$cutim</font> <BR><BR>$mess\";";
}
close POP ;

# ********** limit number of posts ************
if($holn>43) {
   open (POP, "<epa.js");
   @HSD = <POP>;
   close POP;
   $hc=0 ;
   $i=$holn;
   open (FILE, ">epa.js");
   while ($i <= $#HSD) {
      @values=split(']="',$HSD[$i],2);
      if($values[1]) {
         print FILE "hopo[$hc]=\"$values[1]\n" ;
         $hc++;
      }
      $i++ ;
   }
   close FILE;
}

print "Location: index.htm?ver=$holn\n\n";
exit;
