
function initMap() {
	var mazeMap = Maze.map('mazemap-container', {});  
	mazeMap.setView([63.415, 10.41], 14);

	return mazeMap;

	//mazeMap.fitBounds(Maze.latLngBounds(m1.getLatLng(), m2.getLatLng(), m3.getLatLng()));
}

function addRoomMarker(theMap, room) {
	
	var newMarker = Maze.marker(
		[room.geometry.coordinates[1], room.geometry.coordinates[0] ], 
		{icon: Maze.icon(
			{
				iconUrl: getPieChartUrl(room.free_seats / room.total_seats), 
			 	iconSize: [40, 40]
			})
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
	
	newMarker.addTo(theMap);
	
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
		ctx.arc(32, 32, 32, (Math.PI*2)*freeFraction - Math.PI/2, -Math.PI/2);
		ctx.lineTo(32, 32); 
		ctx.fill();
	}
	return canvas.toDataURL("image/png");
}