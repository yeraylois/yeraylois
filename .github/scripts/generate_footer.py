#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_footer.py            *
 *   PURPOSE : GENERATE ANIMATED FOOTER SVG                  *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yerayloissanchez@gmail.com                    *
 *************************************************************/
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets" / "footer"

WIDTH = 840
HEIGHT = 100

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "line": "#9be9a8",
        "pulse": "#9be9a8",
        "text1": "#7d8590",
    },
    "light": {
        "bg": "#ffffff",
        "line": "#36BCF7",
        "pulse": "#36BCF7",
        "text1": "#656d76",
    },
}


def build_footer(theme: str) -> str:
    t = THEMES[theme]

    # SMOOTH WAVE PATH (SINUSOIDAL ON CENTER 40%-60%)
    import math
    line_y = 38
    amplitude = 12
    wave_start = int(WIDTH * 0.40)
    wave_end = int(WIDTH * 0.60)
    steps = 40
    
    points = [f"0,{line_y}", f"{wave_start},{line_y}"]
    for i in range(steps + 1):
        x = wave_start + ((wave_end - wave_start) / steps) * i
        y = line_y + math.sin((i / steps) * 2 * math.pi) * amplitude
        points.append(f"{x:.1f},{y:.1f}")
    points.append(f"{WIDTH},{line_y}")
    wave_path = "M" + " L".join(points)

    path_length = WIDTH + (wave_end - wave_start) * 2
    animated_wave = (
        f'<path d="{wave_path}" fill="none" stroke="{t["pulse"]}" stroke-width="2.8" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<animate attributeName="stroke-dasharray" values="0 {path_length};{path_length} 0" dur="6s" repeatCount="indefinite"/>'
        f'<animate attributeName="stroke-dashoffset" values="{path_length};0" dur="6s" repeatCount="indefinite"/>'
        f'</path>'
    )

    wave_start = int(WIDTH * 0.40)
    wave_end = int(WIDTH * 0.60)
    left_line = (
        f'<line x1="0" y1="{line_y}" x2="{wave_start}" y2="{line_y}" '
        f'stroke="transparent" stroke-width="1"/>'
    )
    right_line = (
        f'<line x1="{wave_end}" y1="{line_y}" x2="{WIDTH}" y2="{line_y}" '
        f'stroke="transparent" stroke-width="1"/>'
    )

    top_line = (
        f'<line x1="40" y1="0" x2="{WIDTH-40}" y2="0" stroke="transparent" stroke-width="1"/>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Footer">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{t['bg']}"/>
  {top_line}
  {left_line}
  {right_line}
  {animated_wave}
  <text x="{WIDTH // 2}" y="72" fill="{t['text1']}" font-size="11.5" font-weight="500" font-family="{FONT}" text-anchor="middle">
    Built with precision by Yeray Lois Sanchez
  </text>
  <text x="{WIDTH // 2}" y="88" fill="{t['text1']}" font-size="10" font-family="{FONT_MONO}" text-anchor="middle" opacity="0.7">
    <animate attributeName="opacity" values="0.7;0.3;0.7" dur="3s" repeatCount="indefinite"/>
    Thanks for visiting
  </text>
</svg>
"""


def generate_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in ("dark", "light"):
        svg = build_footer(theme)
        out = OUTPUT_DIR / f"footer-{theme}.svg"
        out.write_text(svg, encoding="utf-8")

    print(f"Generated footers in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all()
