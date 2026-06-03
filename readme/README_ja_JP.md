## html-press

**html-press** は [plutoprint](https://github.com/nicowillis/plutoprint) レンダリングエンジンを使用して、HTMLから高品質なドキュメントや画像を生成する Dify プラグインです。以下の3つのツールを提供します。

- **HTML→PDF変換** — HTMLをページ分割されたPDFドキュメントとしてレンダリング
- **HTML→PNG変換** — HTMLをPNG画像としてレンダリング
- **QRコード生成** — テキストやURLからQRコード画像を生成

### 機能

- 日本語・絵文字テキストのレンダリング（NotoSansJP・NotoColorEmoji フォント同梱）
- 複数の用紙サイズ対応：A3、A4、A5、B4、B5、Letter、Legal、Ledger
- 縦向き・横向き（PDF）
- デバイススケールによる高DPIレンダリング（PNG）
- PDF・PNG へのカスタムCSS注入
- QRコードの前景色・背景色のカスタマイズ

---

### ツール

#### HTML→PDF変換

HTMLソースコードをPDFドキュメントに変換します。

| パラメータ | 型 | 必須 | デフォルト | 説明 |
| --- | --- | --- | --- | --- |
| `html` | string | はい | — | レンダリングするHTMLソース |
| `page_size` | select | いいえ | `a4` | 用紙サイズ: `a3`, `a4`, `a5`, `b4`, `b5`, `letter`, `legal`, `ledger` |
| `orientation` | select | いいえ | `portrait` | `portrait`（縦）または `landscape`（横） |
| `user_style` | string | いいえ | `""` | HTMLのスタイルに追加で適用するCSS |

#### HTML→PNG変換

HTMLソースコードをPNG画像に変換します。

| パラメータ | 型 | 必須 | デフォルト | 説明 |
| --- | --- | --- | --- | --- |
| `html` | string | はい | — | レンダリングするHTMLソース |
| `width` | number | いいえ | `0`（自動） | 出力幅（ピクセル）。`0` でコンテンツに合わせて自動調整。 |
| `height` | number | いいえ | `0`（自動） | 出力高さ（ピクセル）。`0` でコンテンツに合わせて自動調整。 |
| `device_scale` | number | いいえ | `1` | 高DPI出力用ピクセル密度倍率（例：`2` でRetina相当）。`width`/`height` との同時指定不可。 |
| `user_style` | string | いいえ | `""` | HTMLのスタイルに追加で適用するCSS |

#### QRコード生成

任意のテキストやURLからQRコード画像を生成します。

| パラメータ | 型 | 必須 | デフォルト | 説明 |
| --- | --- | --- | --- | --- |
| `data` | string | はい | — | エンコードするテキスト、URL、メールアドレスなどの文字列 |
| `size` | number | いいえ | `256` | 画像サイズ（ピクセル）。64〜2048の範囲。 |
| `foreground_color` | string | いいえ | `#000000` | QRモジュールの色（16進数、例：`#000000`） |
| `background_color` | string | いいえ | `#FFFFFF` | 背景色（16進数、例：`#FFFFFF`） |

---

### HTMLレンダリングの制約

**plutoprint** はCSSのサブセットを使用します。HTML生成時は以下のルールを守ってください。

1. **必ず背景色を設定する。** `body` 要素に `background-color: #ffffff` を追加してください。透明背景は非対応です。
2. **CSSフレックスボックス・グリッドは使用不可。** `<table>` またはブロックレイアウトを使用してください。
3. **CSS `linear-gradient`・`box-shadow`・`border-radius` は使用不可。** 視覚効果にはインラインSVGを使用してください（SVGは `<linearGradient>`、`<feDropShadow>`、`rx`/`ry` に対応しています）。
4. **図表・グラフにはインラインSVGを使用する。** テキスト以外の視覚的コンテンツには、インラインSVGの使用を推奨します。

---

### プライバシー

このプラグインは、すべてのHTMLコンテンツを Dify プラグインランタイム内でローカル処理します。外部サーバーへのデータ送信は行いません。詳細は [PRIVACY.md](../PRIVACY.md) をご参照ください。
