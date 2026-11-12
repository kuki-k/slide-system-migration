# スライド型カタログ v1

エンジン: `engine/slidekit.py`（型の実装）＋ `engine/render_storyboard.py`（絵コンテJSON→PNG一括描画）
デモ: `demo/storyboard-demo.json` → `demo/out/`（全9型の描画例）

## 共通ルール

- 画面は1920×1080。**下部170pxは字幕帯**で、全型コンテンツを置かない（パイロットの字幕衝突の恒久対策）。
- 色・書体・余白はデザイントークンで統一（背景 #FAF9F6／文字 #1C2430／アクセント #2456C8／強調 #C62F1D／キービジュアル用 黄 #FFC61A・濃紺 #101623）。
- 型は見た目だけを担う。**内容（数字・固有名詞・結論）は絵コンテJSON＝シナリオ側が正本**で、型は内容を発明しない。
- 写真を使う型は `credit`（author／license／source）を渡すとクレジット表記を自動生成する。フリー素材（Wikimedia Commons等、PD／CC0／CC BY／CC BY-SA）はこの形で差し込む。

## 型の一覧

| 型 | 用途 | 主なスロット | 備考 |
|---|---|---|---|
| `title` | 導入。問いと主題を提示 | kicker, title_lines, sub, hero_number, hero_caption | hero_number は右肩に大きく。サムネイルとは別に「動画の顔」 |
| `keyvisual` | キービジュアル。数字と見出しで掴む | badge, headline_lines, hero_number, hero_unit, hero_caption, photo（任意） | 濃紺背景＋黄の特大数字。参考チャンネルの「1枚の設計」を型化したもの。photo を入れると右側に写真 |
| `thumbnail` | YouTubeサムネイル専用（2026-11-12 承認・実装） | badge, headline_lines, hero_number, hero_unit, hero_caption | **1280x720で描画、字幕帯なし**。keyvisual と同じ文法（濃紺＋黄）。絵コンテJSONに混ぜて書けばスライドと一括出力できる |
| `data_rows` | 数値・事実の列挙。距離→時間のような対応表 | kicker, title, rows[{label, dist, value}], point | 1行＝1事実。4〜5行まで |
| `diagram` | 図解。仕組みや関係を自作SVGで見せる | kicker, title, svg_file, caption_lines, chips[{label, value}], point | SVGは場面ごとの作り物。型は枠とチップ・要点帯を提供 |
| `photo_full` | 写真が主役の場面。実物・場所・歴史資料 | photo, bar_title, bar_text, credit | 全面写真＋下部グラデーション帯（字幕帯の上）。クレジットは右上 |
| `photo_side` | 写真＋説明。フリー写真で足りる場面の本命 | kicker, title, photo, credit, bullets, point | 写真は右640px、左に箇条書き3〜4点。図解を作らずに済ませる節約型 |
| `photo_annotate` | 写真にラベルで注釈。「ここがCPU、隣がDRAM」のための型 | kicker, title, photo, photo_ratio, credit, callouts[{x, y, label, lx, ly}], point | 座標は写真に対する%。写真は切り抜き後の状態で座標を指定する。実物の位置関係を教える場面の主役 |
| `compare` | 2項の対比。AとBで何が違うか | kicker, title, left/right{head, sub, lines, foot}, point | foot に結論の数字を置く |
| `point` | 一文の主張。転換点や定義の提示 | kicker, statement_lines, sub | 文字だけの型。使いすぎない（1本に1〜2回） |
| `summary` | まとめと次の疑問 | kicker, title, chips, next_question | chips は要点の再提示。next_question は次回への橋 |

## 写真で足りる場面の考え方（節約の原則）

- 実物・場所・人物・歴史資料が主題なら、図解も3Dも作らず `photo_full`／`photo_side` ＋フリー写真で足りる。今回のパイロットでも写真2場面はこの形で成立した。
- 図解（`diagram`）は「関係や仕組みが写真では伝わらない」ときだけ作る。Blender等のL3はさらに限る（時間変化が理解に必要な場面のみ）という仕様書の線引きと一致。
- 写真の出典・ライセンスは絵コンテJSONに記録し、クレジットは型が自動で表示する（権利台帳と連動）。

## 段階表示（L2）について

- 現行v1は静止画の型のみ。段階表示（要点を1つずつ出す）は、**同じ型で data を段階的に増やした絵コンテを複数枚描く**ことで表現できる（エンジン改修なし）。アニメーション化は次段の課題。

## 使い方

```bash
python3 engine/render_storyboard.py <絵コンテJSON> <出力フォルダ>
```

絵コンテJSONの形式:

```json
{"scenes": [{"id": "S01", "type": "title", "data": { ... 型ごとのスロット ... }}]}
```

写真・SVGの相対パスは絵コンテJSONのあるフォルダ基準。

## キャラクター資産（2026-11-12 登録）

- 置き場: `assets/characters/`、一覧は同フォルダの `characters.json`
- 運用: シリーズごとにペアを固定（コンピューティングの芯=チップ＆電球、基礎知識=フクロウ＆ヒヨコ、AI系=ロボット2体）。デザインは一度作ったものをそのまま使い回し、動画ごとに生成し直さない
- 表情は6種（neutral / explain / puzzled / surprised / nod / laugh）を個別ファイル化済み（チップ＆電球、フクロウ＆ヒヨコ）。ロボットはペアデザインのみで表情セット未生成
- 絵コンテJSONでの指定形式（予定）: `data.characters: [{pair, who, expr, side}]`。slidekitへの描画コンポーネント実装は再検討v2の対話＋テロップ作業と同時に行う

## 対話オーバーレイ（2026-11-12追加、第2話で実証）

任意の型のショットに、キャラ立ち絵（左右）と話者テロップを重ねる仕組み。

- 実装: `slidekit.render_shot(scene, base_dir)` — scene に `cast` / `telop` を付けると通常描画にオーバーレイを注入する。一括描画は `engine/render_dialogue.py <storyboard.json> <out_dir>`（shots[] を描く）。
- cast: `{"left": {"img": 相対パス, "height": px, "active": bool}, "right": {...}}`。発話者は active（通常表示）、聞き手は自動で淡色化（opacity .48＋彩度低下）。
- telop: `{"name": "レン", "color": "accent"|"sun", "text": "ターンの要旨"}`。字幕帯（下部170px）の上にピル型で表示し、ターンごとに差し替える。字幕とは分離。
- `lift: true` を付けるとコンテンツに padding-bottom:290px を足し、要点帯（summary型の「次の疑問」など）がオーバーレイと衝突しない。
- 注意: 対話ショットでは原則 point帯・chips を使わない（下部中央がテロップの領域）。写真場面では cast の height を 175 程度に落とす。
