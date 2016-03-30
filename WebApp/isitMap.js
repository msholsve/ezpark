
var markers = [];
var map;		// MUST be named 'map'
var mapRefresh;

function initMap() {
	var map = Maze.map('mazemap-container', {});  
	map.setView([63.415, 10.41], 14);
	
	return map;
}

function fillMapWithRooms( map, rooms ) {
	
	for(var i = 0; i < markers.length; i++) {
		map.removeLayer(markers[i]);
	}
	for ( var i = 0; i < rooms.length; i++ ) {
	  if(rooms[i].geometry != null) {
			// If the room got coordinates
			markers.push(addRoomMarker(map,	rooms[i]));
	  }
	}
}

function addRoomMarker(map, room) {

	var newMarker;
	
	newMarker = Maze.marker(
		room.geometry.coordinates, 
		{
			icon: Maze.icon(
			{
				iconUrl: getPieChartUrl(room.free_seats, room.total_seats), 
				iconSize: [40, 40]
			}),
			zLevel: room.floorId,
			offZOpacity: 0.6
		}
	);

	newMarker.bindPopup(room.name, {offset: new Maze.Point(0, -12)}); // buggy click handler

	newMarker.on('mouseover', function (e) {
		this.openPopup();
	});
	newMarker.on('mouseout', function (e) {
		this.closePopup();
	});
	newMarker.on("click", function() { 
		changeView( DETAILEDVIEW, {id: room._id, name: room.name} );
	});	

	newMarker.addTo(map);
	
	return newMarker;
}

function getPieChartUrl(freeSeats, numSeats) {
	var RADIUS = 20;
	var freeFraction = freeSeats/numSeats;
	var canvas = document.createElement('canvas');
	canvas.width = RADIUS*2;
	canvas.height = RADIUS*2;
	var ctx = canvas.getContext("2d");	
	
	ctx.beginPath();
	ctx.fillStyle="lightgreen";
	ctx.arc(RADIUS, RADIUS, RADIUS, -Math.PI/2, (Math.PI*2)*freeFraction - Math.PI/2);
	ctx.lineTo(RADIUS, RADIUS); 
	ctx.fill();

	if(freeFraction < 1.0) {
		ctx.beginPath();
		ctx.fillStyle="pink";
		if(freeFraction == 0)
			ctx.arc(RADIUS, RADIUS, RADIUS, 0, Math.PI*2);
		else
			ctx.arc(RADIUS, RADIUS, RADIUS, (Math.PI*2)*freeFraction - Math.PI/2, -Math.PI/2);
		ctx.lineTo(RADIUS, RADIUS); 
		ctx.fill();
	}
	
	ctx.font="13px Arial";
	ctx.fillStyle = "#000000";
	ctx.textAlign="center";
	ctx.textBaseline="middle"; 
	ctx.fillText(freeSeats + "/" + numSeats, RADIUS, RADIUS);
	
	
	return canvas.toDataURL("image/png");
}
