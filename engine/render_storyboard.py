#!/usr/bin/env python3
"""絵コンテJSON → スライドPNG一括描画.

使い方: python3 render_storyboard.py <storyboard.json> <out_dir>
- storyboard.json の scenes[]: {id, type, data} を順に描画する
- 写真/SVGの相対パスは storyboard.json のあるフォルダ基準
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slidekit

CHROME = os.path.expanduser(
    "~/workspace/agent-tools/chs/chrome-headless-shell-linux64/chrome-headless-shell")


def main():
    sb_path = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])
    base_dir = os.path.dirname(sb_path)
    os.makedirs(out_dir, exist_ok=True)
    sb = json.load(open(sb_path, encoding="utf-8"))
    for scene in sb["scenes"]:
        sid = scene["id"]
        html = slidekit.render(scene, base_dir)
        html_path = os.path.join(out_dir, f"{sid}.html")
        png_path = os.path.join(out_dir, f"{sid}.png")
        open(html_path, "w", encoding="utf-8").write(html)
        w, h = slidekit.stage_size(scene["type"])
        r = subprocess.run(
            [CHROME, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", f"--window-size={w},{h}",
             f"--screenshot={png_path}", "--virtual-time-budget=4000",
             "file://" + html_path],
            capture_output=True, text=True)
        ok = os.path.exists(png_path)
        print(f"{sid} ({scene['type']}): {'OK' if ok else 'FAIL ' + r.stderr[-200:]}")
    print("done")


if __name__ == "__main__":
    main()
