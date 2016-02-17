$(document).ready(function() {
    $("#lesesaler").hide();
    $("#info").hide();
    $("#roomImage").hide();
    generateRoomsTable("./rooms.json");

});

function generateRoomsTable(jsonFile) {
    $("#info").show();
    $("#lesesaler").show();
    $.getJSON(jsonFile, function(result) {
	var rooms = result._items;

	var table = "<thead>" +
	    "<tr>" +
	    "<th>Lesesaler</th><th>Ledige plasser</th>" + 
	    "</tr>" + 
	    "</thead>";

	for (var i = 0; i < rooms.length; i++) {
	    table += "<tr>" +
		"<td id=" + rooms[i]._id + ">" +
		rooms[i].name +
		"</td><td>" + String(rooms[i].free_seats) + " / " + String(rooms[i].total_seats) +
		"</td>" +
		"</tr>";
	}

	$("#lesesaler").html(table);

	for (i = 0; i < rooms.length; i++) {
	    bindListItemToRoom(rooms[i]);
	}
    });
}

function bindListItemToRoom(room) {
    $("#" + room._id).click(function () {
	    showRoom(room.name);
    });
}

function showRoom(name) {
    $.getJSON("./room.json", function(result) {
	$("#roomImage").attr("src", "data:image/png;base64," + result.map.file);
    });
    $("#lesesaler").fadeOut("slow");
    $("#info").fadeOut("slow", function() {
	$("#info").html("Du valgte " + name);
	$("#roomImage").fadeIn("slow");
	$("#info").fadeIn("slow");
    });
}

function testRemoteJSON() {
    var root = 'http://jsonplaceholder.typicode.com';
    var data = {url: root + '/posts/1',
		method: 'GET'};
    
    $.ajax(data).then(remoteJSONCallback);
    
}

function remoteJSONCallback( data ) {
    console.log(data);
}
