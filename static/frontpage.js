// scroll div to bottom
var scrollback_div = document.getElementById("scrollback");
scrollback_div.scrollTop = scrollback_div.scrollHeight;

// update console
var msg_num_div = document.getElementById("msg-num");
var msg_num = msg_num_div.innerHTML;
console.log(msg_num);
//console.log(msg_num_div.innerHTML);
var scrollback_text = document.getElementById("scrollback-text");

function fetchJSONFile(path, callback) {
	var httpRequest = new XMLHttpRequest();
	httpRequest.onreadystatechange = function() {
		if (httpRequest.readyState === 4) {
			if (httpRequest.status === 200) {
				var data = JSON.parse(httpRequest.responseText);
				if (callback) callback(data);
			}
		}
	};
	httpRequest.open('GET', path);
	httpRequest.send(); 
}

function append_log(data) {
scrollback_text.innerHTML = scrollback_text.innerHTML + data.join("<br />") + "<br />";
}


function dostuff() {
	fetchJSONFile("/update-sb?msg=" + msg_num, function(data) {
		if (data.length) {
			msg_num = eval(msg_num) + data.length;
			console.log(data);
			append_log(data);
		}
	});
}

setInterval(dostuff, 500);

/*
while (True) {
	sleep(500);
} */
