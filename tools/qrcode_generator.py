import io
from collections.abc import Generator
from typing import Any

import plutoprint
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class QrCodeGeneratorTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        data = tool_parameters.get("data", "")
        if not data or not data.strip():
            yield self.create_text_message("Error: QR code data is required.")
            return

        size = int(tool_parameters.get("size") or 256)
        fg_color = tool_parameters.get("foreground_color") or "#000000"
        bg_color = tool_parameters.get("background_color") or "#FFFFFF"

        for name, value in [("foreground_color", fg_color), ("background_color", bg_color)]:
            if not self._is_valid_hex_color(value):
                yield self.create_text_message(
                    f"Error: Invalid {name} '{value}'. Use hex format like #000000."
                )
                return

        # Escape data for CSS string embedding
        escaped_data = data.replace("\\", "\\\\").replace("'", "\\'")

        margin = max(size // 10, 8)
        html = '<div class="qr"></div>'
        user_style = (
            f"html, body {{ margin: 0; padding: 0; background: {bg_color}; }}"
            f".qr {{ padding: {margin}px; }}"
            f".qr::before {{"
            f"  content: -pluto-qrcode('{escaped_data}', {fg_color});"
            f"  display: block;"
            f"}}"
        )

        try:
            book = plutoprint.Book(media=plutoprint.MEDIA_TYPE_SCREEN)
            book.load_html(html, user_style)

            buf = io.BytesIO()
            book.write_to_png_stream(buf, width=size, height=size)
            blob = buf.getvalue()
        except Exception as e:
            yield self.create_text_message(f"Error generating QR code: {e}")
            return

        yield self.create_blob_message(
            blob=blob,
            meta={
                "mime_type": "image/png",
                "filename": "qrcode.png",
            },
        )

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        if not color.startswith("#"):
            return False
        hex_part = color[1:]
        if len(hex_part) not in (3, 6):
            return False
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False
