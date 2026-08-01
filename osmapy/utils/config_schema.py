"""
Modern Cerberus schema for Osmapy configuration.

This schema validates the structure of config.yaml before it is
converted into dataclasses by load_config().
"""

schema = {
    "osm_api_url": {
        "required": True,
        "type": "string",
        "empty": False,
    },
    "user_agent": {
        "required": True,
        "type": "string",
        "empty": False,
    },
    "window_size": {
        "required": True,
        "type": "list",
        "schema": {"type": "integer"},
        "minlength": 2,
        "maxlength": 2,
    },
    "start_latitude": {
        "required": True,
        "type": "float",
    },
    "start_longitude": {
        "required": True,
        "type": "float",
    },
    "start_zoom": {
        "required": True,
        "type": "integer",
        "min": 0,
        "max": 19,
    },
    "login_name": {
        "required": True,
        "type": "string",
        "empty": False,
    },
    "password": {
        "required": False,
        "nullable": True,
        "type": "string",
    },
    "slippy_tiles": {
        "required": True,
        "type": "list",
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {
                    "required": True,
                    "type": "string",
                    "empty": False,
                },
                "enabled": {
                    "required": True,
                    "type": "boolean",
                },
                "urls": {
                    "required": True,
                    "type": "list",
                    "minlength": 1,
                    "schema": {"type": "string"},
                },
            },
        },
    },
}
