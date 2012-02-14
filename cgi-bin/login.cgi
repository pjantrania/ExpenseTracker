#!/usr/bin/perl
use strict;
use CGI qw/:standard/;
use CGI::Session;
use DBI;
use Config::Simple;

my $cfg = new Config::Simple('../settings.conf');

######
# EDIT settings.conf TO CHANGE
my $db_name = $cfg->param('Database');
my $db_user = $cfg->param('DB-User');
my $db_pass = $cfg->param('DB-Pass');
######

my $dbh = DBI->connect('DBI:mysql:'.$db_name,
		       $db_user,
		       $db_pass) ||
    die "Couldn't connect to database.";

my $cgi = CGI->new;
my $login = param() ? param('uname') : "";
my $pass = param() ? param('pass') : "";
my $query = $dbh->prepare("select id, fname, lname, password FROM auth WHERE fname='$login' AND " .
			  "password=password('$pass')");
$query->execute();

print "Content-type: text/plain\n\n";

if ( $query->rows == 1 ) {
    my $result = $query->fetchrow_hashref();
    my $session = new CGI::Session(undef, $cgi, {Directory=>'/tmp'});
    my $sid = $session->id();
    $session->param("fname", $result->{fname});
    $session->param("lname", $result->{lname});
    $session->param("id", $result->{id});
    print '{"success": "true", "sid": "'.$sid.'"}';
} else {
    print '{"success": "false", "errors": { "reason": "Login failed. Try again." }}';
}
$query->finish;

$dbh->disconnect;
exit;
