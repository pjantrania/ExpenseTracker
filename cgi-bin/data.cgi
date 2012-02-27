#!/usr/bin/perl
use strict;
use JSON;
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
my $action = param() ? param('action') : '';


print "Content-type: application/json\n\n";

if ( $action eq "" ) {
    print "{\"success\": \"false\"}";
} elsif ( $action eq "adddebts" ) {
    my $data = param() ? param('data') : '';
    if ( $data ne '' ) {
	my $debt   = decode_json($data);
	my $uid    = $debt->{uid};
	my $cid    = $debt->{category};
	my $price  = $debt->{price};
	my @owedby = @{$debt->{owedby}};
	my $date   = $debt->{date};
	
	$date =~ s/(\d{2})\/(\d{2})\/(\d{4})/$3-$1-$2/;
	
	$owedby[0] = 0 if ( scalar(@owedby) < 1 );
	for my $owes ( @owedby ) {
	    my $ins = $dbh->prepare_cached(
		'INSERT INTO debts (cid, price, uid, owedby, date) ' .
		'VALUES (?,?,?,?,?)');
	    $ins->execute($cid,$price,$uid,$owes,$date)
		or die $dbh->errstr;
	}
	print "{\"success\": \"true\", \"date\": \"$date\"}";
    }
} elsif ( $action eq "summarize" ) {
    my $sid = param() ? param('sid') : '';
    my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
    my $uid = $session->param("id");
    my $query = $dbh->prepare('select debts.price, auth.fname, ' .
			      'debts.uid from debts, auth '.
			      'where (debts.owedby=? and ' .
			      'auth.id=debts.uid) or ' .
			      '(debts.uid=? and auth.id=debts.owedby)');
    $query->execute($uid,$uid);
    my %totals;
    while ( my @result = $query->fetchrow_array() ) {
	my ($price, $name, $owedto) = @result;
	$totals{$name} = 0 if ( $totals{$name} == undef );
	if ( $owedto != $uid ) {
	    $totals{$name} += $price;
	} else {
	    $totals{$name} -= $price;
	}
    }

    my $query2 = $dbh->prepare('select debts.price, auth.fname ' .
			       'from debts, auth where ' .
			       'debts.uid=? and ' .
			       'auth.id=debts.owedby');
    my $json = "{\"d\": [";
    while ( my ($key, $value) = each(%totals) ) {
	$json .= "{\"name\": \"$key\", \"amount\": \"$value\"},";
    }
    $json =~ s/,$//;
    $json .= "]}";
    print $json;

} elsif ( $action eq "listdebts" ) {
    my $sid = param() ? param('sid') : '';
    my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
    my $uid = $session->param("id");
    my $query = $dbh->prepare('select debts.date, debts.price, '.
			      'auth.fname, categories.name '.
			      'from debts, auth, categories '.
			      'where owedby=? and '.
			      'auth.id=debts.uid and '.
			      'categories.id=debts.cid');
    $query->execute($uid);
    my $json = "{\"d\": [";
    while ( my @result = $query->fetchrow_array() ) {
	$json .= "{\"date\": \"" . $result[0] . "\"," .
	    "\"amount\": \"" . $result[1] . "\"," .
	    "\"to\": \"" . $result[2] . "\"," .
	    "\"category\": \"" . $result[3] . "\"},";
    }
    $json =~ s/,$//;
    $json .= "]}";
    print $json;

} elsif ( $action eq "addcredit" ) {
    my $sid = param() ? param('sid') : '';
    my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
    my $uid = session->param("id");
    my $data = param() ? param('data') : '';
    if ( $data ne '' ) {
	my $credit = decode_json($data);
	my $from   = $credit->{fromid};
	my $date   = $credit->{date};
	my $amount = $credit->{amount};
	my $desc   = $credit->{desc};
	
	my $query = $dbh->prepare_cached('INSERT INTO credits ' .
					 '(fromid, toid, amount, ' .
					 'description, date) ' .
					 'VALUES (?,?,?,?,?)');
	$query->execute($from, $uid, $amount, $desc, $date)
	    or die $dbh->errstr;
	print "{\"success\": \"true\"}";
    }

}

$dbh->disconnect;
exit;
