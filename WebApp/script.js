$(document).ready(function() {
    $("#lesesaler").hide();
    $("#info").hide();
    $("#roomImage").hide();
    $("#button").hide();
    showRooms("http://isit.routable.org/rooms");

});

function showRooms(roomsJSON) {
    $.getJSON(roomsJSON, function(result) {
	$("#info").fadeOut("slow");
	$("#roomImage").fadeOut("slow");
	$("#button").fadeOut("slow", function() {
	    $("#roomImage").html("");
	    $("#info").fadeIn("slow");
	    $("#lesesaler").fadeIn("slow");

	    $("#info").html("Velkommen til iSit. Velg en lesesal for mer informasjon");
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
		bindListItemToRoom(rooms[i]._id, roomsJSON + "/" + rooms[i].name);
	    }
	});
    });
}

function bindListItemToRoom(roomId, roomJSON) {
    $("#" + roomId).click(function () {
	    showRoom(roomJSON);
    });
}

function showRoom(roomJSON) {
    $.getJSON(roomJSON, function(result) {
	$("#lesesaler").fadeOut("slow");
	$("#info").fadeOut("slow", function() {
	    $("#button").fadeIn("slow");
	    $("#roomImage").fadeIn("slow");
	    $("#info").fadeIn("slow");


	    $("#info").html("Du valgte " + result.name);

	    var img = new Image();
	    img.src = "data:image/png;base64," + result.map.file;
	    $("#roomImage").css({
		"height":img.height + "px",
		"width":img.width + "px",
		"background-image":
		"url('" + img.src + "')"
		});

	    
	    for (i = 0; i < result.seats.length; i++) {
		var free = "#00FF00";
		if (result.seats[i].free == false) {
		    free = "#FF0000";
		}

		$("#roomImage").append(
		    $('<div><div>').css({
			position: 'relative',
			top: result.seats[i].location.y + "px",
			left: result.seats[i].location.x + "px",
			width: "10px",
			height: "10px",
			background: free
		    })
		);
	    }

	    $("#button").html("Tilbake");
	    $("#button").click( function () {
		showRooms("http://isit.routable.org/rooms");
	    });
	});
    });
}
