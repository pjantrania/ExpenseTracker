$(document).ready(function(){
    $.ajaxSetup({
      cache: false
      });

  $("#input").submit(function() {
      $("#error").html('');
      var u = $("#uname").val();
      var p = $("#pass").val();
      
      $.post(
	     "cgi-bin/login.cgi",
	     {uname: u, pass: p},
	     function(json) {
	       var result = jQuery.parseJSON(json);
	       if ( result.success === 'true' ) {
		 $.cookie("CGISESSID", result.sid);
		 window.location = 'index.html';
	       }
	       else {
		 $("#error").html('Incorrect.');
	       }
	     }
	     );
      return false;
      
    });
  });
