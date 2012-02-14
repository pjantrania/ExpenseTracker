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

my $item = param() ? param('item') : '';

print "Content-type: application/json\n\n";

if ( $item eq 'categories' ) {
    my $query = $dbh->prepare('select * from categories');
    $query->execute();
    my $response = "{\"categories\": [";

    while ( my $result = $query->fetchrow_hashref() ) {
	$response .= "{\"id\": \"" . $result->{id} . "\", " .
	    "\"name\": \"" . $result->{name} . "\"},";
    }
    $response =~ s/,$//;
    $response .= "]}";
    print $response;
    $query->finish;

} elsif ( $item eq 'people' ) {
    my $sid = param() ? param('sid') : '';
    my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
    my $uid = $session->param("id");
    my $query = $dbh->prepare('select fname, id from auth ' .
			      'where id != ?');
    $query->execute($uid);
    my $response = "{\"people\": [";

    while ( my $result = $query->fetchrow_hashref() ) {
	$response .= "{\"id\": \"" . $result->{id} . "\", " .
	    "\"name\": \"" . $result->{fname} . "\"},";
    }
    $response =~ s/,$//;
    $response .= "]}";
    print $response;
    $query->finish;    
}

$dbh->disconnect;
exit;
