from typing import Callable, Optional

from quart import Quart
from quart_schema import Info, OpenAPIProvider, QuartSchema


class CustomOperationIdOpenAPIProvider(OpenAPIProvider):
    def operation_id(self, method: str, func: Callable) -> Optional[str]:
        return func.__name__


def register_app(app: Quart) -> None:
    title_ = app.config.get("APPLICATION_NAME", "")
    version_ = app.config.get("API_VERSION", "1.0.0")
    api_schema = QuartSchema(
        info=Info(title=title_, version=version_),
        openapi_provider_class=CustomOperationIdOpenAPIProvider,
        conversion_preference="pydantic",
    )

    api_schema.init_app(app)
