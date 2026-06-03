import io
from collections.abc import Generator
from typing import Any

import plutoprint
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.html_to_png import create_book_with_font

PAGE_SIZE_MAP = {
    "a4": plutoprint.PAGE_SIZE_A4,
    "a3": plutoprint.PAGE_SIZE_A3,
    "a5": plutoprint.PAGE_SIZE_A5,
    "b4": plutoprint.PAGE_SIZE_B4,
    "b5": plutoprint.PAGE_SIZE_B5,
    "letter": plutoprint.PAGE_SIZE_LETTER,
    "legal": plutoprint.PAGE_SIZE_LEGAL,
    "ledger": plutoprint.PAGE_SIZE_LEDGER,
}


class HtmlToPdfTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        html_content = tool_parameters.get("html", "")
        if not html_content or not html_content.strip():
            yield self.create_text_message("Error: HTML content is required.")
            return

        page_size_key = tool_parameters.get("page_size", "a4") or "a4"
        orientation = tool_parameters.get("orientation", "portrait") or "portrait"
        user_style = tool_parameters.get("user_style") or ""

        try:
            page_size = PAGE_SIZE_MAP.get(page_size_key, plutoprint.PAGE_SIZE_A4)
            if orientation == "landscape":
                page_size = page_size.landscape()

            book = create_book_with_font(html_content, user_style, page_size=page_size)

            buf = io.BytesIO()
            book.write_to_pdf_stream(buf)
            blob = buf.getvalue()
        except Exception as e:
            yield self.create_text_message(f"Error rendering HTML to PDF: {e}")
            return

        yield self.create_text_message("PDF document has been generated successfully.")
        yield self.create_blob_message(
            blob=blob,
            meta={
                "mime_type": "application/pdf",
                "filename": "output.pdf",
            },
        )
