from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class HtmlPressProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            import plutoprint  # noqa: F401
        except ImportError:
            raise ToolProviderCredentialValidationError(
                "plutoprint library is not installed."
            )
