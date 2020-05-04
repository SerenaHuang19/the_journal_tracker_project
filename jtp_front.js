function submit_form2() {
	var form2 = document.getElementById("form2")
	form2.submit()
}

function submit_form3() {
	var form2 = document.getElementById("form3")
	form2.submit()
}

// function submit_form() {  
// 	var form = document.getElementById("form");         
// 	var formData = new FormData(form);
// 	var searchParams = new URLSearchParams(formData);
// 	var queryString = searchParams.toString();
// 	xmlHttpRqst = new XMLHttpRequest( )
// 	xmlHttpRqst.onload = function(e) {update_page(xmlHttpRqst.response);} 
// 	xmlHttpRqst.open( "GET", "/?" + queryString);
// 	xmlHttpRqst.send();}
// // }

function update_page(response) {
	var div = document.getElementById("plot");
	div.innerHTML = response;
}

function submit_form () {   
	var form = document.getElementById("form");         
	var formData = new FormData(form);
	var searchParams = new URLSearchParams(formData);
	var queryString = searchParams.toString();
	var searchBar = document.getElementById("textbox").value
	queryString = queryString + "?search=" + searchBar
	xmlHttpRqst = new XMLHttpRequest( )
	xmlHttpRqst.onload = function(e) {update_page(xmlHttpRqst.response);} 
	xmlHttpRqst.open( "GET", "/?" + queryString);
	xmlHttpRqst.send();

}


function openCity(cityName) {
  var i;
  var x = document.getElementsByClassName("city");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";  
  }
  document.getElementById(cityName).style.display = "block";  
}
