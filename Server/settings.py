rooms_schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/nicolaiarocci/cerberus) for details.
    'name': {
        'type': 'string',
        'minlength': 1,
        'unique': True,
        'required': True,
    },
    'map': {
        'type': 'media'
    },
    'geometry': {
        'type': 'point'
    },
    'floorId': {
        'type': 'integer'
    },
    'seats': {
        'type': 'list',
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'seats',
                'embeddable': True,
                'field': '_id',
            },
        },
    },
}

rooms = {
    # by default the standard item entry point is defined as
    # '/people/<ObjectId>'. We leave it untouched, and we also enable an
    # additional read-only entry point. This way consumers can also perform
    # GET requests at '/people/<lastname>'.
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'name'
    },

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],

    'embedded_fields': ['seats'],

    'schema': rooms_schema
}

seats_schema = {
    'free': {
        'type': 'boolean',
    },
    'name': {
        'type': 'string',
    },
    'location': {
        'type': 'dict',
        'schema': {
            'x': {'type': 'integer'},
            'y': {'type': 'integer'}
        },
    },
}

seats = {
    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],

    'schema': seats_schema
}

DOMAIN = {
    'rooms': rooms,
    'seats': seats,
}

XML = False
IF_MATCH = False
PAGINATION = False
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
X_DOMAINS = "*"
