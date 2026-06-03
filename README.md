## html-press

**html-press** is a Dify plugin that converts HTML into high-quality documents and images using the [plutoprint](https://github.com/nicowillis/plutoprint) rendering engine. It provides three tools:

- **HTML to PDF** — Render HTML as a paginated PDF document
- **HTML to PNG** — Render HTML as a PNG image
- **QR Code Generator** — Generate QR code images from text or URLs

### Features

- Japanese and emoji text rendering (NotoSansJP + NotoColorEmoji fonts bundled)
- Multiple paper sizes: A3, A4, A5, B4, B5, Letter, Legal, Ledger
- Portrait and landscape orientation for PDF
- High-DPI rendering via device scale for PNG
- Custom CSS injection for both PDF and PNG
- Custom foreground and background colors for QR codes

---

### Tools

#### HTML to PDF

Converts HTML source code to a PDF document.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `html` | string | Yes | — | HTML source to render |
| `page_size` | select | No | `a4` | Paper size: `a3`, `a4`, `a5`, `b4`, `b5`, `letter`, `legal`, `ledger` |
| `orientation` | select | No | `portrait` | `portrait` or `landscape` |
| `user_style` | string | No | `""` | Additional CSS to apply on top of the HTML's own styles |

#### HTML to PNG

Converts HTML source code to a PNG image.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `html` | string | Yes | — | HTML source to render |
| `width` | number | No | `0` (auto) | Output width in pixels. `0` = auto-size from content. |
| `height` | number | No | `0` (auto) | Output height in pixels. `0` = auto-size from content. |
| `device_scale` | number | No | `1` | Pixel density multiplier for high-DPI output (e.g. `2` for Retina). Cannot be combined with `width`/`height`. |
| `user_style` | string | No | `""` | Additional CSS to apply on top of the HTML's own styles |

#### QR Code Generator

Generates a QR code image from any text or URL.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `data` | string | Yes | — | Text, URL, email address, or any string to encode |
| `size` | number | No | `256` | Image size in pixels (64–2048) |
| `foreground_color` | string | No | `#000000` | Hex color of the QR modules (e.g. `#000000`) |
| `background_color` | string | No | `#FFFFFF` | Hex color of the background (e.g. `#FFFFFF`) |

---

### HTML Rendering Constraints

**plutoprint** uses a CSS subset. Follow these rules when writing HTML for this plugin:

1. **Always set a background color.** Add `background-color: #ffffff` to the `body` element. Transparent backgrounds are not supported.
2. **No CSS flexbox or grid.** Use `<table>` or standard block layout instead.
3. **No CSS `linear-gradient`, `box-shadow`, or `border-radius`.** Use inline SVG for visual effects instead — SVG supports `<linearGradient>`, `<feDropShadow>`, and `rx`/`ry` on shapes.
4. **Use inline SVG for all diagrams and charts.** SVG is the recommended approach for any visual content beyond text.

---

### Privacy

All HTML content is processed locally within the Dify plugin runtime. No data is sent to external servers. See [PRIVACY.md](PRIVACY.md) for details.
