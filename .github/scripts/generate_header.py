#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_header.py            *
 *   PURPOSE : GENERATE ZEPHYR BOOT HEADER AND LANGUAGE TABS *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yerayloissanchez@gmail.com                    *
 *************************************************************/
"""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets" / "header"

WIDTH = 840
HEIGHT = 280
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
STEP_SECONDS = 0.42

THEMES = {
    "dark": {"panel": "#010409", "ink": "#f0f6fc", "body": "#c9d1d9", "muted": "#9198a1", "inf": "#9be9a8", "mod": "#a5b0ff", "cursor": "#9be9a8"},
    "light": {"panel": "#f6f8fa", "ink": "#1f2328", "body": "#31373d", "muted": "#59636e", "inf": "#1a7f37", "mod": "#4f5bb3", "cursor": "#36bcf7"},
}

TEXTS = {
    "es": {"profile": "firmware embebido", "focus": "embebidos | automatización | tooling"},
    "en": {"profile": "embedded firmware", "focus": "embedded | automation | tooling"},
}

# (BACKGROUND, TEXT) PER LANGUAGE AND THEME, MATCHING THE SECTION ACCENTS
TABS = {
    ("en", "dark"): ("#9be9a8", "#0d1117"),
    ("en", "light"): ("#5c6bc0", "#ffffff"),
    ("es", "dark"): ("#b85a3c", "#ffffff"),
    ("es", "light"): ("#b85a3c", "#ffffff"),
}
TAB_LABELS = {"en": ("EN", "ENGLISH"), "es": ("ES", "ESPAÑOL")}


def log_line(y: int, step: int, ts: str, module: str, message: str, t: dict) -> str:
    return (
        f'<g class="l" style="animation-delay:{step * STEP_SECONDS:.2f}s">'
        f'<text x="32" y="{y}" font-family="{FONT_MONO}" font-size="14">'
        f'<tspan fill="{t["muted"]}">[{ts}]</tspan> '
        f'<tspan fill="{t["inf"]}">&lt;inf&gt;</tspan> '
        f'<tspan fill="{t["mod"]}">{module}:</tspan></text>'
        f'<text x="{WIDTH - 32}" y="{y}" fill="{t["body"]}" font-family="{FONT_MONO}" font-size="14" '
        f'text-anchor="end">{html.escape(message)}</text></g>'
    )


def build_header(theme: str, lang: str) -> str:
    t = THEMES[theme]
    tx = TEXTS[lang]
    lines = [
        log_line(70, 2, "00:00:00.000,000", "board", "udc_computer_engineering, 2021-2025", t),
        log_line(94, 3, "00:00:00.003,417", "profile", tx["profile"], t),
        log_line(196, 5, "00:00:00.012,880", "focus", tx["focus"], t),
        log_line(220, 6, "00:00:00.013,102", "upstream", "zephyrproject-rtos/zephyr#108610 merged", t),
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Yeray Lois Sanchez: {html.escape(tx['profile'])}, {html.escape(tx['focus'])}">
  <style>
    .l {{ opacity: 0; animation: boot 220ms ease-out forwards; }}
    .c {{ animation: blink 1s steps(1) 6; animation-delay: {7 * STEP_SECONDS:.2f}s; }}
    @keyframes boot {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .l {{ opacity: 1; animation: none; }} .c {{ animation: none; }} }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{t['panel']}"/>
  <g class="l" style="animation-delay:{STEP_SECONDS:.2f}s" fill="{t['muted']}" font-family="{FONT_MONO}" font-size="14">
    <text x="32" y="42">***</text>
    <text x="{WIDTH // 2}" y="42" text-anchor="middle">Booting Zephyr OS build yeraylois</text>
    <text x="{WIDTH - 32}" y="42" text-anchor="end">***</text>
  </g>
  {lines[0]}
  {lines[1]}
  <g class="l" style="animation-delay:{4 * STEP_SECONDS:.2f}s">
    <text x="{WIDTH // 2}" y="160" fill="{t['ink']}" font-family="{FONT}" font-size="46" font-weight="700" letter-spacing="-1" text-anchor="middle">Yeray Lois Sanchez</text>
  </g>
  {lines[2]}
  {lines[3]}
  <g class="l" style="animation-delay:{7 * STEP_SECONDS:.2f}s">
    <text x="32" y="254" fill="{t['body']}" font-family="{FONT_MONO}" font-size="14">uart:~$</text>
    <rect class="c" x="100" y="241" width="9" height="16" fill="{t['cursor']}"/>
  </g>
</svg>
"""


def build_tab(theme: str, lang: str) -> str:
    background, text = TABS[(lang, theme)]
    code, label = TAB_LABELS[lang]
    width = 44 + 18 + len(label) * 9
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-label="{label}">
  <rect width="{width}" height="28" rx="3" fill="{background}"/>
  <path d="M3 0H44V28H3A3 3 0 0 1 0 25V3A3 3 0 0 1 3 0Z" fill="#555555"/>
  <text x="22" y="18" fill="#ffffff" font-family="{FONT}" font-size="11" font-weight="700" letter-spacing="1.5" text-anchor="middle">{code}</text>
  <text x="{44 + (width - 44) // 2}" y="18" fill="{text}" font-family="{FONT}" font-size="11" font-weight="700" letter-spacing="1.5" text-anchor="middle">{label}</text>
</svg>
"""


def generate_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for lang in TEXTS:
            (OUTPUT_DIR / f"header-{theme}-{lang}.svg").write_text(build_header(theme, lang), encoding="utf-8")
            (OUTPUT_DIR / f"tab-{theme}-{lang}.svg").write_text(build_tab(theme, lang), encoding="utf-8")
    print(f"Generated header and language tabs in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all()
