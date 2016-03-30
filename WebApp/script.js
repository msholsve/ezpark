var roomsJSON = 'http://isit.routable.org/api/rooms';
var currentView;
var selectedTab;
var refresh;
var map;		// MUST be named 'map'

const LISTVIEW = 1;
const MAPVIEW = 2;
const DETAILEDVIEW = 3;

$( document ).ready( function() {
	
	$.ajaxSetup({ cache: false });

	$( '#info' ).html( 'Velkommen til Isit!' );
	$( '#map' ).html( "<div id='mazemap-container'></div>" );

	$( '#backButton' ).hide();
	$( '#list' ).hide();
	$( '#map' ).hide();
	$( '#roomImage' ).hide();

	$( '#listViewTab' ).click( function() {
	selectedTab = LISTVIEW;
	changeView( LISTVIEW, {} );
	});

	$( '#mapViewTab' ).click( function() {
	selectedTab = MAPVIEW;
	changeView( MAPVIEW, {} );
	});

	currentView = LISTVIEW;
	selectedTab = LISTVIEW;
	transitionIn( currentView, {} );
} );

function changeView( view, params ) {
	transitionOut( transitionIn, view, params );
	currentView = view;
}


function transitionOut( transitionIn, view, params ) {
	var selector;

	console.log( 'transition from', currentView, 'to', view );

	switch( currentView ) {
	case LISTVIEW:
	selector = '.list-view';
	break;

	case MAPVIEW:
	selector = '.map-view';
	break;

	case DETAILEDVIEW:
	clearInterval( refresh );
	selector = '.detailed-view';
	break;

	default:
	console.error( 'view is invalid' );
	}

	$( selector ).fadeOut( 'fast' );
	$( selector ).promise().done( function() {
	transitionIn( view, params );
	} );
}


function transitionIn( view, params ) {
	if ( view == LISTVIEW ) {
	showListView().done( function() {
		$( '.list-view' ).fadeIn( 'fast' );
	} );

	} else if ( view == MAPVIEW ) {
	$( '.map-view' ).fadeIn( 'fast' );
	showMapView();

	} else if ( view == DETAILEDVIEW ) {
	showDetailedView( params.id, params.name ).done( function() {
		$( '.detailed-view' ).fadeIn( 'fast' );
	} );
	}
}


function showListView() {
	return $.getJSON( roomsJSON, function( result ) {
	$( '#info' ).html( 'Velg en lesesal fra listen for mer informasjon' );
	fillListWithRooms( result._items );
	});
}


function showMapView() {
	map = initMap();
	$.getJSON( roomsJSON, function( result ) {
		$( '#info' ).html( 'Velg en lesesal fra listen for mer informasjon' );
		fillMapWithRooms( map, result._items );
	});
}

function showDetailedView( id, name ) {
	return $.getJSON( roomsJSON + '/' + id, function( roomWithImage ) { 
	
	$( '#info' ).html( 'Du valgte ' + roomWithImage.name );
	$( '#backButton' ).html( 'Tilbake' );
	clearSeatsOnImage();
	
	var img = new Image();
	img.src = 'data:image/png;base64,' + roomWithImage.map.file;
	img.onload = function () {
		setImageAsBackground( img );
		placeSeatsOnImage( roomWithImage.seats );
	}
	
	refresh = setInterval( function () {
		$.getJSON(
		roomsJSON + '/' + id + '?projection={"map":%200}',
		function ( roomWithoutImage ) {
			clearSeatsOnImage();
			placeSeatsOnImage( roomWithoutImage.seats );
			
		})
	}, 1000);
	
	$( '#backButton' ).unbind();
	$( '#backButton' ).click( function () {
		changeView( selectedTab );
	} );
	} );
}


function fillListWithRooms( rooms ) {
	var table = '<thead>' +
	'<tr>' +
	'<th>Lesesaler</th><th>Ledige plasser</th>' + 
	'</tr>' + 
	'</thead>';

	for ( var i = 0; i < rooms.length; i++ ) {
	table += '<tr>' +
		'<td id=' + rooms[i]._id + '>' +
		rooms[i].name +
		'</td><td>' + String(rooms[i].free_seats) + ' / ' + String(rooms[i].total_seats) +
		'</td>' +
		'</tr>';
	}

	$( '#list' ).html( table );

	for ( i = 0; i < rooms.length; i++ ) {
	bindListItemToRoom( rooms[i]._id, rooms[i].name );
	}
}

function fillMapWithRooms( map, rooms ) {
	for ( var i = 0; i < rooms.length; i++ ) {
	if(rooms[i].geometry != null) {	
		// If the room got coordinates	
		addRoomMarker(map,	rooms[i]); 
	}
	}
}

function bindListItemToRoom( id, name ) {
	$( '#' + id ).click( function () {
	changeView( DETAILEDVIEW, {id: id, name: name} );
	} );
}


function setImageAsBackground( image ) {
	$( '#roomImage' ).css({
	'position': 'relative',
	'height':image.naturalHeight + 'px',
	'width':image.naturalWidth + 'px',
	'background-image':"url('" + image.src + "')"
	});
}


function placeSeatsOnImage( seats ) {
	var free;
	for ( i = 0; i < seats.length; i++ ) {
	free = '#00FF00';
	if ( seats[i].free == false ) {
		free = '#FF0000';
	}
	
	$( '#roomImage' ).append(
		$( '<div><div>' ).css({
		position: 'absolute',
		top: seats[i].location.y + 'px',
		left: seats[i].location.x + 'px',
		width: '10px',
		height: '10px',
		background: free
		})
	);
	}
}


function clearSeatsOnImage() {
	$( '#roomImage' ).html( '' );
}
