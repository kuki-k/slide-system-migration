#!/usr/bin/env python3
"""slidekit — スライド「型」ライブラリ v1.

設計原則:
- シナリオ（絵コンテJSON）が正本。型は見た目だけを担い、内容は発明しない。
- 全型で下部170pxを「字幕帯」として確保し、コンテンツを置かない（パイロットの字幕衝突対策）。
- 写真は data の photo スロットに差し込む。credit があればクレジット表記を自動生成する。
- 色・書体・余白はデザイントークンで一元管理する。
"""
import html as _html
import os

TOKENS_CSS = """
:root{
  --bg:#FAF9F6; --ink:#1C2430; --accent:#2456C8; --accent-soft:#E8EEFB;
  --impact:#C62F1D; --sun:#FFC61A; --muted:#5A6472; --line:#D8D3C8;
  --card:#FFFFFF; --dark:#101623; --dark-ink:#F4F2EC;
  --font:'Noto Sans CJK JP',sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden}
body{font-family:var(--font);background:var(--bg);color:var(--ink)}
.stage{width:1920px;height:1080px;display:flex;flex-direction:column;
  padding:78px 108px 0 108px}
.content{flex:1;display:flex;flex-direction:column;min-height:0}
.subband{height:170px;flex:none}  /* 字幕帯: ここには何も置かない */
.kicker{font-size:30px;font-weight:700;color:var(--accent);letter-spacing:.14em;margin-bottom:26px}
h1{font-size:74px;font-weight:800;line-height:1.28}
h1 .impact{color:var(--impact)}
.sub{font-size:36px;color:var(--muted);line-height:1.55;margin-top:30px}
.point{margin-top:auto;background:var(--accent-soft);border-left:10px solid var(--accent);
  padding:26px 34px;font-size:35px;font-weight:700;line-height:1.5}
.chips{display:flex;gap:22px;flex-wrap:wrap}
.chip{background:var(--card);border:2px solid var(--line);border-radius:16px;
  padding:20px 30px;font-size:33px;font-weight:700}
.chip b{color:var(--accent)}
.credit{font-size:22px;color:#EDEBE4;text-shadow:0 1px 6px rgba(0,0,0,.65)}
"""


def esc(s):
    return _html.escape(str(s), quote=True)


# 型ごとの描画サイズ（幅, 高さ）。サムネイルだけ YouTube 標準の 1280x720。
STAGE_SIZES = {"thumbnail": (1280, 720)}


def stage_size(scene_type):
    return STAGE_SIZES.get(scene_type, (1920, 1080))


def _page(body, extra_css="", dark=False):
    bg = "background:var(--dark);color:var(--dark-ink)" if dark else ""
    return (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'>"
            f"<style>{TOKENS_CSS}{extra_css}</style></head>"
            f"<body style='{bg}'><div class='stage' style='{bg}'>"
            f"<div class='content'>{body}</div><div class='subband'></div>"
            f"</div></body></html>")


def _credit_text(credit):
    if not credit:
        return ""
    parts = [credit.get("author", ""), credit.get("license", "")]
    lic = "（" + "／".join(p for p in [credit.get("license", ""), credit.get("source", "")] if p) + "）" if credit.get("license") else ""
    return f"写真：{credit.get('author','')}{lic}"


def _uri(path, base_dir):
    p = path if os.path.isabs(path) else os.path.join(base_dir, path)
    return "file://" + os.path.abspath(p)


# ---------------------------------------------------------------- title
def t_title(d, base_dir):
    hero = ""
    if d.get("hero_number"):
        hero = (f"<div class='hero'><div class='hero-num'>{esc(d['hero_number'])}</div>"
                f"<div class='hero-cap'>{esc(d.get('hero_caption',''))}</div></div>")
    title = "<br>".join(esc(x) for x in d["title_lines"])
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<div class='title-flex'><h1>{title}</h1>{hero}</div>"
            f"<div class='sub'>{esc(d.get('sub',''))}</div>")
    css = (".content{justify-content:center;padding-bottom:60px}"
           ".title-flex{display:flex;align-items:flex-start;gap:60px}"
           ".hero{margin-left:auto;text-align:right;flex:none}"
           ".hero-num{font-size:96px;font-weight:800;color:var(--accent);line-height:1.15}"
           ".hero-cap{font-size:30px;color:var(--muted);margin-top:10px}")
    return _page(body, css)


# ---------------------------------------------------------------- keyvisual
def t_keyvisual(d, base_dir):
    photo = ""
    if d.get("photo"):
        photo = (f"<div class='kv-photo'><img src='{_uri(d['photo'], base_dir)}'>"
                 f"<div class='kv-credit'>{esc(_credit_text(d.get('credit')))}</div></div>")
    lines = "<br>".join(esc(x) for x in d["headline_lines"])
    body = (f"<div class='kv-badge'>{esc(d.get('badge',''))}</div>"
            f"<div class='kv-flex'><div class='kv-main'>"
            f"<h1 class='kv-h'>{lines}</h1>"
            f"<div class='kv-num'>{esc(d.get('hero_number',''))}<span class='kv-unit'>{esc(d.get('hero_unit',''))}</span></div>"
            f"<div class='kv-cap'>{esc(d.get('hero_caption',''))}</div>"
            f"</div>{photo}</div>")
    css = (".stage{padding-top:64px}"
           ".kv-badge{display:inline-block;align-self:flex-start;background:var(--sun);color:#1C2430;"
           "font-size:30px;font-weight:800;padding:12px 26px;border-radius:10px;margin-bottom:44px}"
           ".kv-flex{display:flex;gap:56px;align-items:center}"
           ".kv-main{flex:1}"
           ".kv-h{font-size:92px;color:var(--dark-ink)}"
           ".kv-num{font-size:150px;font-weight:800;color:var(--sun);line-height:1.1;margin-top:36px}"
           ".kv-unit{font-size:52px;color:var(--dark-ink);margin-left:18px}"
           ".kv-cap{font-size:38px;color:#C9CEDA;margin-top:22px}"
           ".kv-photo{flex:none;width:600px}"
           ".kv-photo img{width:600px;height:600px;object-fit:cover;border-radius:24px;"
           "border:6px solid rgba(255,255,255,.25)}"
           ".kv-credit{margin-top:12px}.kv-credit{font-size:22px;color:#9AA3B5}")
    return _page(body, css, dark=True)


# ---------------------------------------------------------------- thumbnail
def t_thumbnail(d, base_dir):
    """サムネイル専用型（1280x720、字幕帯なし）。承認済みサムネイル型v1の実装。
    keyvisual と同じ文法（濃紺＋黄）だが、YouTubeサムネイルの実寸で描く。"""
    lines = "<br>".join(esc(x) for x in d["headline_lines"])
    num = ""
    if d.get("hero_number"):
        num = (f"<div class='th-num'>{esc(d['hero_number'])}"
               f"<span class='th-unit'>{esc(d.get('hero_unit',''))}</span></div>")
    img = ""
    if d.get("image"):
        img = (f"<img class='th-img' src='{_uri(d['image'], base_dir)}'>")
    body = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'>"
            f"<style>{TOKENS_CSS}"
            "html,body{width:1280px;height:720px}"
            "body{background:var(--dark);color:var(--dark-ink)}"
            ".th-wrap{width:1280px;height:720px;display:flex;flex-direction:column;"
            "justify-content:center;padding:56px 64px}"
            ".th-badge{display:inline-block;align-self:flex-start;background:var(--sun);"
            "color:var(--dark);font-weight:800;font-size:30px;padding:10px 22px;"
            "border-radius:10px;margin-bottom:28px}"
            ".th-h{font-size:84px;line-height:1.22;font-weight:800}"
            ".th-num{font-size:120px;font-weight:800;color:var(--sun);line-height:1.05;"
            "margin-top:26px;white-space:nowrap}"
            ".th-unit{font-size:52px;color:var(--dark-ink);margin-left:16px}"
            ".th-cap{font-size:32px;color:#C9CEDA;margin-top:18px}"
            ".th-wrap{position:relative}"
            ".th-img{position:absolute;right:30px;bottom:0;height:405px}"
            ".th-h,.th-num,.th-cap,.th-badge{position:relative;z-index:2}"
            f"</style></head><body><div class='th-wrap'>{img}"
            f"<div class='th-badge'>{esc(d.get('badge',''))}</div>"
            f"<div class='th-h'>{lines}</div>{num}"
            f"<div class='th-cap'>{esc(d.get('hero_caption',''))}</div>"
            f"</div></body></html>")
    return body


# ---------------------------------------------------------------- data_rows
def t_data_rows(d, base_dir):
    rows = ""
    for r in d["rows"]:
        rows += (f"<div class='row'><div class='row-label'>{esc(r['label'])}</div>"
                 f"<div class='row-dist'>{esc(r.get('dist',''))}</div>"
                 f"<div class='row-arrow'>→</div>"
                 f"<div class='row-value'>{esc(r['value'])}</div></div>")
    point = f"<div class='point'>{esc(d['point'])}</div>" if d.get("point") else ""
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<h1 class='small'>{esc(d['title'])}</h1>"
            f"<div class='rows'>{rows}</div>{point}")
    css = ("h1.small{font-size:58px;margin-bottom:44px}"
           ".rows{display:flex;flex-direction:column;gap:20px}"
           ".row{display:flex;align-items:center;background:var(--card);"
           "border:2px solid var(--line);border-radius:16px;padding:24px 34px}"
           ".row-label{font-size:38px;font-weight:800;width:430px}"
           ".row-dist{font-size:32px;color:var(--muted);width:340px}"
           ".row-arrow{font-size:34px;color:var(--accent);width:70px;text-align:center}"
           ".row-value{font-size:42px;font-weight:800;color:var(--accent)}")
    return _page(body, css)


# ---------------------------------------------------------------- diagram
def t_diagram(d, base_dir):
    svg = ""
    if d.get("svg_file"):
        p = d["svg_file"] if os.path.isabs(d["svg_file"]) else os.path.join(base_dir, d["svg_file"])
        svg = open(p, encoding="utf-8").read()
    caps = "<br>".join(esc(x) for x in d.get("caption_lines", []))
    chips = "".join(
        f"<div class='chip'>{esc(c['label'])} <b>{esc(c['value'])}</b></div>"
        for c in d.get("chips", []))
    point = f"<div class='point'>{esc(d['point'])}</div>" if d.get("point") else ""
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<h1 class='small'>{esc(d['title'])}</h1>"
            f"<div class='diagram'>{svg}</div>"
            f"<div class='cap'>{caps}</div>"
            f"<div class='chips'>{chips}</div>{point}")
    css = ("h1.small{font-size:58px;margin-bottom:18px}"
           ".diagram{display:flex;justify-content:center;padding:6px 0}"
           ".diagram svg{max-width:1500px;max-height:430px;width:auto;height:auto}"
           ".cap{font-size:32px;color:var(--muted);text-align:center;line-height:1.5;margin:10px 0 26px}"
           ".chips{justify-content:center}")
    return _page(body, css)


# ---------------------------------------------------------------- photo_full
def t_photo_full(d, base_dir):
    credit = _credit_text(d.get("credit"))
    credit_html = f"<div class='credit pf-credit'>{esc(credit)}</div>" if credit else ""
    body = (f"<img class='pf-img' src='{_uri(d['photo'], base_dir)}'>"
            f"{credit_html}"
            f"<div class='pf-bar'><div class='pf-title'>{esc(d['bar_title'])}</div>"
            f"<div class='pf-text'>{esc(d.get('bar_text',''))}</div></div>")
    css = (".stage{padding:0}.content{position:relative}"
           ".pf-img{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}"
           ".pf-credit{position:absolute;top:34px;right:40px;z-index:3}"
           ".pf-bar{position:absolute;left:0;right:0;bottom:170px;z-index:2;"
           "background:linear-gradient(transparent,rgba(10,14,22,.90) 55%);"
           "padding:64px 108px 36px}"
           ".pf-title{font-size:56px;font-weight:800;color:#fff}"
           ".pf-text{font-size:34px;color:#E4E1D8;margin-top:14px;line-height:1.5}")
    return _page(body, css)


# ---------------------------------------------------------------- photo_side
def t_photo_side(d, base_dir):
    bullets = "".join(f"<li>{esc(b)}</li>" for b in d.get("bullets", []))
    credit = _credit_text(d.get("credit"))
    credit_html = f"<div class='ps-credit'>{esc(credit)}</div>" if credit else ""
    point = f"<div class='point'>{esc(d['point'])}</div>" if d.get("point") else ""
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<div class='ps-flex'><div class='ps-text'>"
            f"<h1 class='small'>{esc(d['title'])}</h1>"
            f"<ul class='ps-ul'>{bullets}</ul></div>"
            f"<div class='ps-photo'><img src='{_uri(d['photo'], base_dir)}'>{credit_html}</div></div>"
            f"{point}")
    css = ("h1.small{font-size:56px;margin-bottom:36px}"
           ".ps-flex{display:flex;gap:56px;align-items:flex-start}"
           ".ps-text{flex:1}"
           ".ps-ul{list-style:none}"
           ".ps-ul li{font-size:37px;line-height:1.5;padding:18px 0 18px 34px;position:relative;"
           "border-bottom:2px solid var(--line)}"
           ".ps-ul li:before{content:'';position:absolute;left:0;top:38px;width:14px;height:14px;"
           "border-radius:50%;background:var(--accent)}"
           ".ps-photo{flex:none;width:640px}"
           ".ps-photo img{width:640px;height:560px;object-fit:cover;border-radius:20px}"
           ".ps-credit{font-size:22px;color:var(--muted);margin-top:12px;text-shadow:none}")
    return _page(body, css)


# ---------------------------------------------------------------- photo_annotate
def t_photo_annotate(d, base_dir):
    """写真にラベル（コールアウト）を付ける型。「ここにあるのがCPU」のための型。
    callouts: {x, y, label, lx, ly} — すべて写真に対する%座標。x,y が指す位置、
    lx,ly がラベル中心。座標は写真の切り抜き後の状態で指定する。"""
    lines, dots, chips = "", "", ""
    for c in d["callouts"]:
        lines += (f"<line x1='{c['x']}' y1='{c['y']}' x2='{c['lx']}' y2='{c['ly']}'/>")
        dots += (f"<circle class='dot' cx='{c['x']}' cy='{c['y']}' r='1.15'/>"
                 f"<circle class='dot-in' cx='{c['x']}' cy='{c['y']}' r='0.5'/>")
        chips += (f"<div class='callout' style='left:{c['lx']}%;top:{c['ly']}%'>"
                  f"{esc(c['label'])}</div>")
    credit = _credit_text(d.get("credit"))
    credit_html = f"<div class='pa-credit'>{esc(credit)}</div>" if credit else ""
    point = f"<div class='point'>{esc(d['point'])}</div>" if d.get("point") else ""
    ratio = d.get("photo_ratio", "4/3")
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<h1 class='small'>{esc(d['title'])}</h1>"
            f"<div class='pa-wrap'><div class='pa-photo' style='aspect-ratio:{ratio}'>"
            f"<img src='{_uri(d['photo'], base_dir)}'>"
            f"<svg viewBox='0 0 100 100' preserveAspectRatio='none'>{lines}{dots}</svg>"
            f"{chips}</div>{credit_html}</div>{point}")
    css = ("h1.small{font-size:54px;margin-bottom:22px}"
           ".pa-wrap{display:flex;flex-direction:column;align-items:center}"
           ".pa-photo{position:relative;height:596px}"
           ".pa-photo img{height:596px;width:auto;display:block;border-radius:14px}"
           ".pa-photo svg{position:absolute;inset:0;width:100%;height:100%}"
           ".pa-photo svg line{stroke:var(--accent);stroke-width:.45}"
           ".pa-photo svg .dot{fill:#fff;stroke:var(--accent);stroke-width:.45}"
           ".pa-photo svg .dot-in{fill:var(--impact)}"
           ".callout{position:absolute;transform:translate(-50%,-50%);"
           "background:#fff;border:3px solid var(--accent);border-radius:999px;"
           "padding:9px 20px;font-size:27px;font-weight:800;white-space:nowrap;"
           "box-shadow:0 3px 10px rgba(16,22,35,.25)}"
           ".pa-credit{align-self:flex-end;font-size:22px;color:var(--muted);margin-top:10px}")
    return _page(body, css)


# ---------------------------------------------------------------- compare
def t_compare(d, base_dir):
    def card(side, cls):
        lines = "".join(f"<li>{esc(x)}</li>" for x in side.get("lines", []))
        return (f"<div class='cmp-card {cls}'><div class='cmp-head'>{esc(side['head'])}</div>"
                f"<div class='cmp-sub'>{esc(side.get('sub',''))}</div>"
                f"<ul>{lines}</ul>"
                f"<div class='cmp-foot'>{esc(side.get('foot',''))}</div></div>")
    point = f"<div class='point'>{esc(d['point'])}</div>" if d.get("point") else ""
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<h1 class='small'>{esc(d['title'])}</h1>"
            f"<div class='cmp-flex'>{card(d['left'],'left')}{card(d['right'],'right')}</div>"
            f"{point}")
    css = ("h1.small{font-size:58px;margin-bottom:40px}"
           ".cmp-flex{display:flex;gap:36px}"
           ".cmp-card{flex:1;background:var(--card);border:2px solid var(--line);"
           "border-radius:20px;padding:40px 44px}"
           ".cmp-card.right{border-color:var(--accent)}"
           ".cmp-head{font-size:46px;font-weight:800}"
           ".cmp-sub{font-size:30px;color:var(--muted);margin:8px 0 24px}"
           ".cmp-card ul{list-style:none}"
           ".cmp-card li{font-size:34px;line-height:1.55;padding:10px 0}"
           ".cmp-foot{margin-top:26px;padding-top:22px;border-top:2px solid var(--line);"
           "font-size:38px;font-weight:800;color:var(--accent)}")
    return _page(body, css)


# ---------------------------------------------------------------- point
def t_point(d, base_dir):
    lines = "<br>".join(esc(x) for x in d["statement_lines"])
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<div class='stmt'>{lines}</div>"
            f"<div class='sub'>{esc(d.get('sub',''))}</div>")
    css = (".stmt{font-size:84px;font-weight:800;line-height:1.45;margin-top:110px}"
           ".stmt .impact{color:var(--impact)}")
    return _page(body, css)


# ---------------------------------------------------------------- summary
def t_summary(d, base_dir):
    chips = "".join(f"<div class='chip'>{esc(c)}</div>" for c in d.get("chips", []))
    nxt = ""
    if d.get("next_question"):
        nxt = (f"<div class='point'><span class='nq-label'>次の疑問</span>"
               f"{esc(d['next_question'])}</div>")
    body = (f"<div class='kicker'>{esc(d.get('kicker',''))}</div>"
            f"<h1>{esc(d['title'])}</h1>"
            f"<div class='chips sum-chips'>{chips}</div>{nxt}")
    css = (".sum-chips{margin-top:56px}.sum-chips .chip{font-size:36px;padding:26px 34px}"
           ".nq-label{color:var(--accent);margin-right:22px}")
    return _page(body, css)


TEMPLATES = {
    "title": t_title,
    "keyvisual": t_keyvisual,
    "thumbnail": t_thumbnail,
    "data_rows": t_data_rows,
    "diagram": t_diagram,
    "photo_full": t_photo_full,
    "photo_side": t_photo_side,
    "photo_annotate": t_photo_annotate,
    "compare": t_compare,
    "point": t_point,
    "summary": t_summary,
}


def render(scene, base_dir):
    t = scene["type"]
    if t not in TEMPLATES:
        raise ValueError(f"unknown template type: {t}")
    return TEMPLATES[t](scene.get("data", {}), base_dir)


# ---------------------------------------------------------------- dialogue overlay
# 対話形式のショット用: キャラ立ち絵（左右）＋話者テロップを、任意の型の上に重ねる。
# 話者テロップは字幕帯（下部170px）の上に置き、発話中キャラは明るく、聞き手は淡くする。
DIALOGUE_CSS = """
.cast-layer{position:fixed;inset:0;z-index:60;pointer-events:none}
.cast{position:absolute;bottom:182px}
.cast img{display:block;border-radius:18px}
.cast.left{left:30px}
.cast.right{right:30px}
.cast.dim{opacity:.48;filter:saturate(.7)}
.telop{position:absolute;left:50%;transform:translateX(-50%);bottom:198px;
  display:flex;align-items:center;gap:18px;background:rgba(16,22,35,.93);
  border-radius:999px;padding:14px 32px 14px 16px;max-width:1140px}
.telop-name{font-size:29px;font-weight:800;padding:9px 22px;border-radius:999px;white-space:nowrap}
.telop-name.accent{background:var(--accent);color:#fff}
.telop-name.sun{background:var(--sun);color:#1C2430}
.telop-text{font-size:32px;font-weight:700;color:#F4F2EC;white-space:nowrap}
"""


def render_shot(scene, base_dir):
    """scene に cast / telop があれば対話オーバーレイを重ねて返す。
    cast: {"left": {img, height, active}, "right": {...}}
    telop: {"name": "レン", "color": "accent"|"sun", "text": "要旨"}
    """
    page = render(scene, base_dir)
    cast = scene.get("cast")
    telop = scene.get("telop")
    if not cast and not telop:
        return page
    parts = ["<div class='cast-layer'>"]
    if cast:
        for side in ("left", "right"):
            c = cast.get(side)
            if not c:
                continue
            h = int(c.get("height", 250))
            cls = "cast " + side + ("" if c.get("active") else " dim")
            parts.append(
                f"<div class='{cls}'><img src='{_uri(c['img'], base_dir)}' "
                f"style='height:{h}px'></div>")
    if telop:
        parts.append(
            f"<div class='telop'><div class='telop-name "
            f"{esc(telop.get('color', 'accent'))}'>{esc(telop['name'])}</div>"
            f"<div class='telop-text'>{esc(telop['text'])}</div></div>")
    parts.append("</div>")
    inject = f"<style>{DIALOGUE_CSS}</style>" + "".join(parts)
    if scene.get("lift"):
        # 下部に要点帯などがある型では、コンテンツを持ち上げてオーバーレイと衝突させない
        inject += "<style>.content{padding-bottom:290px}</style>"
    return page.replace("</body>", inject + "</body>")
