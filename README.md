# slide-system-migration

教育動画「勉強用メモ」のスライドテンプレートシステム（実働コード）の移行先リポジトリ。

絵コンテJSON（storyboard）から、1920×1080のスライド画像と対話シーン（キャラ＋話者テロップ付き）を一括描画する。テンプレートは11種（title / keyvisual / data_rows / diagram / photo_full / photo_side / photo_annotate / compare / point / summary / thumbnail）＋対話オーバーレイ。

## 構成

| パス | 内容 |
|---|---|
| `engine/slidekit.py` | テンプレート本体＋デザイントークン＋対話オーバーレイレンダラ |
| `engine/render_storyboard.py` | CLI: `python3 engine/render_storyboard.py <storyboard.json> <out_dir>` |
| `engine/render_dialogue.py` | 対話版CLI（shots＋cast＋telop を描画） |
| `catalog.md` | 型カタログと使用ルール（正本） |
| `assets/characters/characters.json` | キャラクター資産のマニフェスト（ペア・シリーズ割当・声・表情一覧） |
| `demo/` | デモ用 storyboard 3種 |

## 実行環境の前提

- Python 3.11+（標準ライブラリのみ）
- スクリーンショットに **Chrome for Testing の headless shell** を使う。現行コードはパスが `~/workspace/agent-tools/chs/chrome-headless-shell-linux64/chrome-headless-shell` にハードコードされている（`render_storyboard.py` / `render_dialogue.py` の `CHROME` 定数）。**移植時は環境変数化するのが課題**。
- フォント: Noto Sans CJK JP（静的フォント。バリアブルフォントは描画で化ける事例あり）

## このリポジトリに含まれていないもの

- キャラクター画像（PNG 53点）とデモ用写真はバイナリのため未収録。`assets/characters/characters.json` のパス構成に従い、別途配置すること（GitHub Webアップロードまたはローカルクローン経由）。
- 動画の合成（音声・字幕・FFmpeg）は別工程で、このリポジトリの範囲外。

## 来歴

本番稼働中の作業コピーは `~/workspace/video-pilot/slide-template-system/`（Muse のVM内）。本リポジトリは、その保全と可搬化（パス依存の解消、デモ描画のスモークテスト追加など）のための移行先。
