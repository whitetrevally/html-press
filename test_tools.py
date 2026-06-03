"""Unit tests for html-press tools - tests actual tool classes with mocked dify_plugin."""

import struct
import sys
import types
from dataclasses import dataclass, field
from typing import Any

# Mock dify_plugin before importing tools
dify_plugin = types.ModuleType("dify_plugin")
dify_plugin_entities = types.ModuleType("dify_plugin.entities")
dify_plugin_entities_tool = types.ModuleType("dify_plugin.entities.tool")


@dataclass
class ToolInvokeMessage:
    type: str
    blob: bytes = b""
    meta: dict = field(default_factory=dict)
    text: str = ""


class Tool:
    def create_blob_message(self, blob: bytes, meta: dict) -> ToolInvokeMessage:
        return ToolInvokeMessage(type="blob", blob=blob, meta=meta)

    def create_text_message(self, text: str) -> ToolInvokeMessage:
        return ToolInvokeMessage(type="text", text=text)


dify_plugin.Tool = Tool
dify_plugin_entities_tool.ToolInvokeMessage = ToolInvokeMessage
dify_plugin.entities = dify_plugin_entities
dify_plugin.entities.tool = dify_plugin_entities_tool

sys.modules["dify_plugin"] = dify_plugin
sys.modules["dify_plugin.entities"] = dify_plugin_entities
sys.modules["dify_plugin.entities.tool"] = dify_plugin_entities_tool

# Now import the actual tool classes
from tools.html_to_png import HtmlToPngTool
from tools.html_to_pdf import HtmlToPdfTool
from tools.qrcode_generator import QrCodeGeneratorTool

PNG_HEADER = b"\x89PNG\r\n\x1a\n"
PDF_HEADER = b"%PDF-"


def invoke(tool, params: dict[str, Any]) -> list[ToolInvokeMessage]:
    return list(tool._invoke(params))


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Parse PNG IHDR chunk to get (width, height) in pixels."""
    assert data[:8] == PNG_HEADER, "Not a valid PNG"
    # IHDR is always the first chunk: bytes 8-11 = length, 12-15 = 'IHDR', 16-19 = width, 20-23 = height
    w, h = struct.unpack(">II", data[16:24])
    return w, h


# ============================================================
# html_to_png
# ============================================================

def test_png_basic():
    msgs = invoke(HtmlToPngTool(), {"html": "<h1>Hello</h1>"})
    assert len(msgs) == 1 and msgs[0].type == "blob"
    assert msgs[0].blob[:8] == PNG_HEADER
    assert msgs[0].meta == {"mime_type": "image/png"}
    w, h = png_dimensions(msgs[0].blob)
    assert w > 0 and h > 0
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_png_empty_html():
    msgs = invoke(HtmlToPngTool(), {"html": ""})
    assert len(msgs) == 1 and msgs[0].type == "text"
    assert "Error" in msgs[0].text
    print("  OK: got error message")


def test_png_with_width():
    msgs = invoke(HtmlToPngTool(), {"html": "<p>Test</p>", "width": 640})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 640, f"Expected width=640, got {w}"
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_png_with_width_and_height():
    msgs = invoke(HtmlToPngTool(), {"html": "<p>Test</p>", "width": 640, "height": 480})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 640, f"Expected width=640, got {w}"
    assert h == 480, f"Expected height=480, got {h}"
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_png_with_device_scale():
    msgs = invoke(HtmlToPngTool(), {"html": "<p>Hi-DPI</p>", "width": 400, "height": 300, "device_scale": 2.0})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 800, f"Expected width=800 (400*2), got {w}"
    assert h == 600, f"Expected height=600 (300*2), got {h}"
    print(f"  OK: {w}x{h}px (400x300 @ 2x), {len(msgs[0].blob)} bytes")


def test_png_device_scale_without_dimensions():
    msgs = invoke(HtmlToPngTool(), {"html": "<p>Auto size</p>", "device_scale": 2.0})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w > 0 and h > 0
    print(f"  OK: {w}x{h}px (auto size @ 2x), {len(msgs[0].blob)} bytes")


def test_png_with_user_style():
    msgs = invoke(HtmlToPngTool(), {
        "html": "<div class='box'>Styled</div>",
        "user_style": ".box { background: red; padding: 20px; }",
        "width": 320,
    })
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 320, f"Expected width=320, got {w}"
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_png_no_params():
    msgs = invoke(HtmlToPngTool(), {"html": "<p>Defaults</p>"})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w > 0 and h > 0
    print(f"  OK: {w}x{h}px (auto), {len(msgs[0].blob)} bytes")


# ============================================================
# html_to_pdf
# ============================================================

def test_pdf_basic():
    msgs = invoke(HtmlToPdfTool(), {"html": "<h1>Hello PDF</h1>"})
    assert len(msgs) == 1 and msgs[0].type == "blob"
    assert msgs[0].blob[:5] == PDF_HEADER
    assert msgs[0].meta == {"mime_type": "application/pdf"}
    print(f"  OK: {len(msgs[0].blob)} bytes (A4)")


def test_pdf_empty_html():
    msgs = invoke(HtmlToPdfTool(), {"html": "  "})
    assert len(msgs) == 1 and msgs[0].type == "text"
    assert "Error" in msgs[0].text
    print(f"  OK: got error message")


def test_pdf_page_sizes():
    for size_key in ["a4", "a3", "a5", "b4", "b5", "letter", "legal", "ledger"]:
        msgs = invoke(HtmlToPdfTool(), {"html": f"<p>{size_key}</p>", "page_size": size_key})
        assert msgs[0].type == "blob" and msgs[0].blob[:5] == PDF_HEADER
        print(f"  OK: {size_key} = {len(msgs[0].blob)} bytes")


def test_pdf_landscape():
    msgs = invoke(HtmlToPdfTool(), {"html": "<p>Landscape</p>", "orientation": "landscape"})
    assert msgs[0].type == "blob" and msgs[0].blob[:5] == PDF_HEADER
    print(f"  OK: {len(msgs[0].blob)} bytes (landscape)")


def test_pdf_with_user_style():
    msgs = invoke(HtmlToPdfTool(), {
        "html": "<p>Styled PDF</p>",
        "user_style": "p { color: blue; font-size: 24px; }",
    })
    assert msgs[0].type == "blob" and msgs[0].blob[:5] == PDF_HEADER
    print(f"  OK: {len(msgs[0].blob)} bytes (with user_style)")


# ============================================================
# qrcode_generator
# ============================================================

def test_qr_basic():
    msgs = invoke(QrCodeGeneratorTool(), {"data": "https://example.com"})
    assert len(msgs) == 1 and msgs[0].type == "blob"
    assert msgs[0].blob[:8] == PNG_HEADER
    assert msgs[0].meta == {"mime_type": "image/png"}
    w, h = png_dimensions(msgs[0].blob)
    assert w == 256, f"Expected default size 256, got {w}"
    assert h > 0
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_qr_empty_data():
    msgs = invoke(QrCodeGeneratorTool(), {"data": ""})
    assert msgs[0].type == "text" and "Error" in msgs[0].text
    print("  OK: got error message")


def test_qr_custom_size():
    msgs = invoke(QrCodeGeneratorTool(), {"data": "test", "size": 512})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 512, f"Expected size 512, got {w}"
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes")


def test_qr_custom_colors():
    msgs = invoke(QrCodeGeneratorTool(), {
        "data": "colored",
        "foreground_color": "#FF0000",
        "background_color": "#FFFF00",
    })
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 256
    print(f"  OK: {w}x{h}px (red on yellow), {len(msgs[0].blob)} bytes")


def test_qr_invalid_color():
    msgs = invoke(QrCodeGeneratorTool(), {"data": "test", "foreground_color": "red"})
    assert msgs[0].type == "text" and "Invalid" in msgs[0].text
    print("  OK: got validation error")


def test_qr_special_chars():
    msgs = invoke(QrCodeGeneratorTool(), {"data": "it's a \\test"})
    assert msgs[0].type == "blob"
    w, h = png_dimensions(msgs[0].blob)
    assert w == 256
    print(f"  OK: {w}x{h}px, {len(msgs[0].blob)} bytes (special chars)")


# ============================================================
# Run all
# ============================================================

if __name__ == "__main__":
    tests = [
        ("html_to_png: basic", test_png_basic),
        ("html_to_png: empty html", test_png_empty_html),
        ("html_to_png: width", test_png_with_width),
        ("html_to_png: width+height", test_png_with_width_and_height),
        ("html_to_png: device_scale", test_png_with_device_scale),
        ("html_to_png: device_scale (auto size)", test_png_device_scale_without_dimensions),
        ("html_to_png: user_style", test_png_with_user_style),
        ("html_to_png: all defaults", test_png_no_params),
        ("html_to_pdf: basic", test_pdf_basic),
        ("html_to_pdf: empty html", test_pdf_empty_html),
        ("html_to_pdf: page_sizes", test_pdf_page_sizes),
        ("html_to_pdf: landscape", test_pdf_landscape),
        ("html_to_pdf: user_style", test_pdf_with_user_style),
        ("qrcode: basic", test_qr_basic),
        ("qrcode: empty data", test_qr_empty_data),
        ("qrcode: custom size", test_qr_custom_size),
        ("qrcode: custom colors", test_qr_custom_colors),
        ("qrcode: invalid color", test_qr_invalid_color),
        ("qrcode: special chars", test_qr_special_chars),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"[TEST] {name}")
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {passed + failed} total")
