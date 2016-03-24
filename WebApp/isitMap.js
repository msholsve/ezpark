
function initMap() {
	var map = Maze.map('mazemap-container', {});  
	map.setView([63.415, 10.41], 14);
	return map;
}


function addRoomMarker(map, room) {
	
	var newMarker = Maze.marker(
		room.geometry.coordinates, 
		{icon: Maze.icon(
			{
				iconUrl: getPieChartUrl(room.free_seats / room.total_seats), 
			 	iconSize: [40, 40]
			}),
			zLevel: 1,			// TODO: fikse zlevel til riktig floor
			offZOpacity: 0.6	// Shows trasparent icon when the user views the wrong floor
		}
	);

	newMarker.bindPopup(room.name);
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

function getPieChartUrl(freeFraction) {
	var canvas = document.createElement('canvas');
	canvas.width = 64;
	canvas.height = 64;
	var ctx = canvas.getContext("2d");	
	
	ctx.beginPath();
	ctx.fillStyle="lightgreen";
	ctx.arc(32, 32, 32, -Math.PI/2, (Math.PI*2)*freeFraction - Math.PI/2);
	ctx.lineTo(32, 32); 
	ctx.fill();

	if(freeFraction < 1.0) {
		ctx.beginPath();
		ctx.fillStyle="red";
		if(freeFraction == 0)
			ctx.arc(32, 32, 32, 0, Math.PI*2);
		else
			ctx.arc(32, 32, 32, (Math.PI*2)*freeFraction - Math.PI/2, -Math.PI/2);
		ctx.lineTo(32, 32); 
		ctx.fill();
	}
	return canvas.toDataURL("image/png");
}
