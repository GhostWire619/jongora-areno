JAZZMIN_SETTINGS["show_ui_builder"] = True

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'VALIDATOR_URL': None,
    'OPERATIONS_SORTER': 'alpha',
    'DISPLAY_OPERATION_ID': False,
    'PERSIST_AUTH': True,
    'DOC_EXPANSION': 'list',
    'DEFAULT_MODEL_RENDERING': 'model',
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch',
    ],
    'DEEP_LINKING': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'FETCH_SCHEMA_WITH_QUERY': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
    },
    'SWAGGER_UI_DIST': 'STATIC_URL/swagger-ui/',
    'SWAGGER_UI_FAVICON_HREF': 'STATIC_URL/favicon.ico',
    'DEFAULT_INFO': 'Myapp.urls.schema_view.info',
    'DEFAULT_API_URL': 'http://localhost:8000/swagger/',
    'CUSTOM_CSS': 'css/swagger-custom.css',
}

# Redoc settings
REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
}

customColorPalette = [ ]