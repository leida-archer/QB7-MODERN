#!/usr/bin/perl
use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standard);

my $query = new CGI;
my $indices_str = $query->param("indices");

# Parse comma-separated indices into a hash for quick lookup
my %to_delete;
foreach my $idx (split(/,/, $indices_str)) {
    $idx =~ s/\D//g;
    $to_delete{$idx} = 1 if $idx ne '';
}

# Read current epa.js
open(POP, "<epa.js") or die "Cannot open epa.js: $!";
my @lines = <POP>;
close POP;

# Collect all hopo entries (each may span a single line)
# Entry format: hopo[N]="...";
my @entries;
my $current = '';
foreach my $line (@lines) {
    if ($line =~ /^hopo\[\d+\]/) {
        if ($current ne '') {
            push @entries, $current;
        }
        $current = $line;
    } elsif ($current ne '') {
        $current .= $line;
    }
}
push @entries, $current if $current ne '';

# Filter out deleted entries and re-index
my @kept;
for (my $i = 0; $i <= $#entries; $i++) {
    unless ($to_delete{$i}) {
        push @kept, $entries[$i];
    }
}

# Rewrite epa.js with new indices
open(FILE, ">epa.js") or die "Cannot write epa.js: $!";
for (my $i = 0; $i <= $#kept; $i++) {
    my $entry = $kept[$i];
    $entry =~ s/^hopo\[\d+\]/hopo[$i]/;
    # Ensure clean line breaks between entries
    $entry =~ s/^\s+//;
    $entry =~ s/\s+$//;
    print FILE "\n" if $i > 0;
    print FILE "$entry\n";
}
close FILE;

print "Content-Type: text/plain\n\n";
print "OK";
