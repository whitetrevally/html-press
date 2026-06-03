import io
import math
import os
from collections.abc import Generator
from typing import Any

import plutoprint
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_assets")
_FONTS: dict[str, bytes] = {}


def _build_style_tag() -> str:
    return (
        "<style>"
        "@font-face { font-family: 'NotoSansJP'; src: url('notosansjp.ttf') format('truetype'); }"
        "@font-face { font-family: 'NotoColorEmoji'; src: url('notocoloremoji.ttf') format('truetype'); }"
        "* { font-family: NotoSansJP, NotoColorEmoji, Arial, Helvetica, sans-serif !important; }"
        "body { background-color: #ffffff; }"
        "</style>"
    )


def _get_font(name: str) -> bytes | None:
    if name not in _FONTS:
        path = os.path.join(_ASSETS_DIR, name)
        try:
            with open(path, "rb") as f:
                _FONTS[name] = f.read()
        except FileNotFoundError:
            _FONTS[name] = b""
    return _FONTS[name] or None


class _FontFetcher(plutoprint.ResourceFetcher):
    FONT_MAP = {
        "notosansjp": "NotoSansJP-Regular.ttf",
        "notocoloremoji": "NotoColorEmoji.ttf",
    }

    def fetch_url(self, url: str) -> plutoprint.ResourceData | None:
        lower = url.lower()
        for key, filename in self.FONT_MAP.items():
            if key in lower:
                data = _get_font(filename)
                if data:
                    return plutoprint.ResourceData(data, "font/ttf", "")
        return None


def _inject_style(html: str) -> str:
    tag = _build_style_tag()
    lower = html.lower()
    head_end = lower.find("</head>")
    if head_end != -1:
        return html[:head_end] + tag + html[head_end:]
    body_start = lower.find("<body")
    if body_start != -1:
        return html[:body_start] + tag + html[body_start:]
    return tag + html


def create_book_with_font(html: str, user_style: str, page_size=None) -> plutoprint.Book:
    if page_size is not None:
        book = plutoprint.Book(page_size)
    else:
        book = plutoprint.Book(media=plutoprint.MEDIA_TYPE_SCREEN)

    book.custom_resource_fetcher = _FontFetcher()
    book.load_html(_inject_style(html), user_style)
    return book


class HtmlToPngTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        html_content = tool_parameters.get("html", "")
        if not html_content or not html_content.strip():
            yield self.create_text_message("Error: HTML content is required.")
            return

        width = tool_parameters.get("width") or None
        height = tool_parameters.get("height") or None
        device_scale = tool_parameters.get("device_scale") or None
        user_style = tool_parameters.get("user_style") or ""
        if device_scale and (width or height):
            yield self.create_text_message(
                "Error: device_scale cannot be used together with width/height. "
                "Use either device_scale alone or width/height."
            )
            return

        try:
            blob = self._render_png(html_content, user_style, width, height, device_scale)
        except Exception as e:
            yield self.create_text_message(f"Error rendering HTML to PNG: {e}")
            return

        yield self.create_blob_message(
            blob=blob,
            meta={
                "mime_type": "image/png",
                "filename": "output.png",
            },
        )

    def _render_png(
        self,
        html: str,
        user_style: str,
        width: float | None,
        height: float | None,
        device_scale: float | None,
    ) -> bytes:
        book = create_book_with_font(html, user_style)

        if device_scale and device_scale != 1.0:
            return self._render_with_scale(book, device_scale)

        buf = io.BytesIO()
        kwargs: dict[str, Any] = {}
        if width:
            kwargs["width"] = int(width)
        if height:
            kwargs["height"] = int(height)
        book.write_to_png_stream(buf, **kwargs)
        return buf.getvalue()

    def _render_with_scale(
        self,
        book: plutoprint.Book,
        device_scale: float,
    ) -> bytes:
        width = math.ceil(book.get_document_width())
        height = math.ceil(book.get_document_height())

        canvas_w = int(width * device_scale)
        canvas_h = int(height * device_scale)
        canvas = plutoprint.ImageCanvas(canvas_w, canvas_h)
        canvas.scale(device_scale, device_scale)
        book.render_document(canvas)

        buf = io.BytesIO()
        canvas.write_to_png_stream(buf)
        return buf.getvalue()
