TORTOISE_ORM = {
    "connections": {"default": "sqlite://test.db"},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
