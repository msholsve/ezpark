$(document).ready(function() {
    $.ajaxSetup({ cache: false });
    $("#lesesaler").hide();
    $("#info").hide();
    $("#roomImage").hide();
    $("#button").hide();
    showRooms();

});

var roomsJSON = "http://isit.routable.org/api/rooms";

function showRooms() {
    $.getJSON(roomsJSON, function(result) {
	$("#info").fadeOut("slow");
	$("#roomImage").fadeOut("slow");
	$("#button").fadeOut("slow", function() {
	    clearSeatsOnImage();
	    $("#info").fadeIn("slow");
	    $("#lesesaler").fadeIn("slow");

	    $("#info").html("Velkommen til iSit. Velg en lesesal for mer informasjon");
	    fillTableWithRooms(result._items);
	});
    });
}

function fillTableWithRooms(rooms) {
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
	bindListItemToRoom(rooms[i]._id, rooms[i].name);
    }
}

function bindListItemToRoom(id, name) {
    $("#" + id).click(function () {
	showRoom(id, name);
    });
}

function showRoom(id, name) {
    $.getJSON(roomsJSON + "/" + id, function(roomWithImage) {
	$("#lesesaler").fadeOut("slow");
	$("#info").fadeOut("slow", function() {
	    $("#button").fadeIn("slow");
	    $("#roomImage").fadeIn("slow");
	    $("#info").fadeIn("slow");

	    $("#info").html("Du valgte " + roomWithImage.name);

	    var img = new Image();
	    img.src = "data:image/png;base64," + roomWithImage.map.file;
	    img.onload = function () {
		setImageAsBackground(img);
		placeSeatsOnImage(roomWithImage.seats);
	    }

	    var refresh = setInterval( function () {
		$.getJSON(
		    roomsJSON + "/" + id + "?projection={\"map\":%200}",
		    function (roomWithoutImage) {
			clearSeatsOnImage();
			placeSeatsOnImage(roomWithoutImage.seats);
			
		    })
	    }, 1000);

	    $("#button").html("Tilbake");
	    $("#button").click( function () {
		clearInterval(refresh);
		showRooms(roomsJSON);
	    });
	});
    });
}

function setImageAsBackground(image) {
    $("#roomImage").css({
	"height":image.naturalHeight + "px",
	"width":image.naturalWidth + "px",
	"background-image":"url('" + image.src + "')"
	});
}

function placeSeatsOnImage(seats) {
    var free;
    for (i = 0; i < seats.length; i++) {
	free = "#00FF00";
	if (seats[i].free == false) {
	    free = "#FF0000";
	}
	
	$("#roomImage").append(
	    $('<div><div>').css({
		position: 'relative',
		top: seats[i].location.y + "px",
		left: seats[i].location.x + "px",
		width: "10px",
		height: "10px",
		background: free
	    })
	);
    }
}

function clearSeatsOnImage() {
    $("#roomImage").html("");
}
