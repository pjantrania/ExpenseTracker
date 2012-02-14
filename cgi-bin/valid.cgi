#!/usr/bin/perl
use strict;
use CGI qw/:standard/;
use CGI::Session;
use DBI;

my $cgi = CGI->new;

my $sid = param() ? param('sid') : '';

if ( $sid ne '' ) {
    print "Content-type: text/plain\n\n";
    my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
    if ( param('logout') eq 'true' ) {
	$session->delete();
	print "{\"success\": \"true\"}";
    } else {
	my $name = $session->param("fname");
	my $id = $session->param("id");
	if ( $name ne '' ) {
	    print "{\"success\": \"true\", ".
		"\"name\": \"$name\", ".
		"\"id\": \"$id\"}";
	} else {
	    print "{\"success\": \"false\"}";
	}
    }

}
