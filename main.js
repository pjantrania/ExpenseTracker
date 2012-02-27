$.ajaxSetup ({
	cache: false
    });

var sid = $.cookie('CGISESSID');
var name;
var userid;
$(function() {
    if ( sid == null )
      window.location = 'login.html';
    $.post(
	   "cgi-bin/valid.cgi",
	   {sid: sid},
	   function(response) {
	     var json = jQuery.parseJSON(response);
	     if ( json.success === 'true' ) {
	       $("#top").html('<p>Welcome, ' + json.name + ' '
			      + '<a href="javascript:logout()" id=logout>' +
			      'Log out</a></p>');
	       name = json.name;
	       userid = json.id;
	     } else
	       $("#content").html('<p>Not logged in</p>');
	   }
	   );
  });

$(document).ready( function() {
    $('#message').fadeTo(0,0);

    // Populate category dropdown
    $("#category").ready( function() {
	var options = $("#category");
	$.getJSON("cgi-bin/populate.cgi", {item: 'categories'},
		  function(result) {
		    
		    var cats = result.categories;
		    for ( var i = 0; i < cats.length; i++ ) {
		      options.append($("<option />")
				     .val(cats[i].id)
				     .text(cats[i].name));
		    }
		  });
      });
    
    // Populate owed-by checkboxes
    var numpeople = 0;
    $("#people").ready( function() {
	var box = $("#people");
	$.getJSON("cgi-bin/populate.cgi", {item: 'people', sid: sid},
		  function(result) {
		    var peeps = result.people;
		    window.people = peeps;
		    for ( var i = 0; i < peeps.length; i++ ) {
		      
		      box.append($(document.createElement("input"))
				 .attr({
				   type: 'checkbox',
				       class: 'ownedby',
				       id: 'check'+peeps[i].id,
				       value: peeps[i].id
				       })
				 ).append("<label for=\"check"+
					  peeps[i].id +
					  "\">" +
					  peeps[i].name +
					  "</label><br />");
		    }
		  });
      });
    
    // Submit debt
    $("#debtform").submit( function() {
	var debt = new Object();
	debt.uid = userid;
	debt.owedby = new Array();
	debt.category = $("#category").val();
	$('[type=checkbox]:checked').each( function() {
	    debt.owedby.push($(this).val());
	    numpeople++;
	  });
	debt.date = $("#date").val();
	debt.price = $("#price").val();
	if ( debt.price.search(/^\$?\d+(\.\d{2})?$/) == -1 ) {
	  alert('Invalid price');
	  $("#price").focus();
	  return false;
	} else {
	  debt.price.replace(/\$/,'');
	  if ( $("[type=radio]:checked").val() === 'split' ) {
	    alert(numpeople);
	    debt.price = debt.price/numpeople;
	  }
	}
	var json = JSON.stringify(debt);
	
	$.post(
	       'cgi-bin/data.cgi',
	       {action: "adddebts", data: json},
	       function(response) {
		 if ( response.success === 'true' ) {
		   flashMsg('Submitted');
		   $("#debtform").each(function() {
		       this.reset();
		     });
		 } else
		   alert('There has been a problem');
	       },
	       "json"
	       );
	updateSummary();
	return false;
      });

    $("#debttable").ready(function() {
	updateSummary();
      });
  });

function logout() {
  var sid = $.cookie('CGISESSID');
  $.post(
	 "cgi-bin/valid.cgi",
	 {sid: sid, logout: 'true'},
	 function(response) {
	   var json = jQuery.parseJSON(response);
	   if ( json.success === 'true' ) {
	     window.location = 'login.html';
	     $.cookie('CGISESSID', null);
	   } else {
	     $("#content").html('<p>Had trouble logging out. Refresh</p>');
	     $.cookie('CGISESSID', null);
	   }
	 }
	 );
  
}

function updateSummary() {
  var sid = $.cookie('CGISESSID');
  $("#debttable").html("<tr><th>Date</th><th>To</th>" +
		       "<th>For</th><th>Amount</th></tr>");
  $("#summarylist").html("");
  $.getJSON("cgi-bin/data.cgi",{action: 'summarize', sid: sid},
	    function(result) {
	      for ( var i = 0; i < result.d.length; i++ ) {
		var item = result.d[i];
		var price = parseFloat(item.amount);
		var litext;
		if ( price > 0 )
		  litext = "<li>You owe " + item.name +
		    " $" + price.toFixed(2) + ".</li>";
		else if ( price < 0 )
		  litext = "<li>" + item.name + " owes you " +
		    "$" + Math.abs(price).toFixed(2) + ". <a href=\"#\" onclick=\"settle("+item.name+"); return false;\">Settle</a></li>";
		else
		  litext = "<li>You and " + item.name +
		    " are square.</li>";
		
		$("#summarylist").append(litext);
	      }
	      /*
		for ( var i = 0; i < result.d.length; i++ ) {
		var row = result.d[i];		    
		var rcls = i % 2 == 0 ? "even" : "odd";
		var rowtext = "<tr class=\""+rcls+"\">"+
		  "<td>"+row.date+"</td>" +
		  "<td>"+row.to+"</td>" +
		  "<td>"+row.category+"</td>" +
		  "<td>"+row.amount+"</td>" +
		  "</tr>";
		$("#debttable tr:last").after(rowtext);
	      }
	      */
	    });
}

function flashMsg(message) {
    $("#message").text(message);
    $("#message").fadeTo("fast",1)
      .animate({opacity:1.0}, 1750).fadeTo("slow",0);
}

function toggle(elem) {
  $("#"+elem).toggle();
}
