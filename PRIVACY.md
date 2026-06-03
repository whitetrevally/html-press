## Privacy Policy

**html-press** is a document rendering plugin for the Dify platform.

### Data Processing

This plugin processes HTML content, text, and URLs provided by the user solely for the purpose of generating PDF documents, PNG images, and QR code images.

- **No data is transmitted to external servers.** All rendering is performed locally within the Dify plugin runtime environment using the `plutoprint` library.
- **No data is stored.** The plugin does not retain, log, or persist any input content or generated output beyond the scope of a single tool invocation.
- **No personal information is collected.** The plugin does not collect, analyze, or share any user data.

### Third-Party Libraries

This plugin uses the following third-party library for rendering:

- [plutoprint](https://github.com/nicowillis/plutoprint) — A local HTML/CSS rendering library. All processing occurs in-process with no network access.

### Bundled Fonts

The plugin includes the following open-source fonts for rendering Japanese text and emoji:

- **Noto Sans JP** — Licensed under the [SIL Open Font License 1.1](https://scripts.sil.org/OFL)
- **Noto Color Emoji** — Licensed under the [SIL Open Font License 1.1](https://scripts.sil.org/OFL)

### Contact

For questions or concerns about this plugin, please open an issue at:  
[https://github.com/whitetrevally/html-press/issues](https://github.com/whitetrevally/html-press/issues)
