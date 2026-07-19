#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_stack.py             *
 *   PURPOSE : GENERATE EDITORIAL TECH STACK INDEX           *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yerayloissanchez@gmail.com                    *
 *************************************************************/
"""

from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets" / "stack"
ICONS_DIR = ROOT / "assets" / "icons" / "catalog"
TECH_YAML = ROOT / "assets" / "tech_icons.yml"
STACK_DATA = ROOT / "assets" / "stack" / "recent.json"

WIDTH = 840
HEIGHT = 128
ICON_SIZE = 26

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
PROJECT = "YERAYLOIS GITHUB PROFILE"
AUTHOR = "Yeray Lois Sanchez"
EMAIL = "yerayloissanchez@gmail.com"
BANNER_WIDTH = 61

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "text1": "#e6edf3",
        "text2": "#7d8590",
        "border": "#30363d",
        "accent": "#9be9a8",
    },
    "light": {
        "bg": "#ffffff",
        "text1": "#1f2328",
        "text2": "#656d76",
        "border": "#d1d9e0",
        "accent": "#36BCF7",
    },
}

TECH_COLORS = {
    "bash": "#4EAA25",
    "c": "#555555",
    "git": "#F05032",
    "python": "#3572A5",
    "docker": "#2496ED",
    "ansible": "#EE0000",
    "angular": "#DD0031",
    "typescript": "#3178C6",
    "javascript": "#F7DF1E",
    "java": "#007396",
    "go": "#00ADD8",
    "rust": "#DEA584",
    "html": "#E34F26",
    "css": "#1572B6",
    "kubernetes": "#326CE5",
    "terraform": "#7B42BC",
    "nginx": "#009639",
    "postgresql": "#336791",
    "mysql": "#4479A1",
    "mongodb": "#47A248",
    "redis": "#DC382D",
    "sqlite": "#0F80CC",
    "react": "#61DAFB",
    "vue": "#4FC08D",
    "nodejs": "#339933",
    "django": "#092E20",
    "flask": "#000000",
    "fastapi": "#009688",
    "spring": "#6DB33F",
    "express": "#404040",
    "laravel": "#FF2D20",
    "rails": "#CC0000",
    "flutter": "#02569B",
    "ionic": "#3880FF",
    "electron": "#47848F",
    "tauri": "#24C8D8",
    "qt": "#41CD52",
    "gtk": "#7FE719",
    "aws": "#FF9900",
    "azure": "#0078D4",
    "gcp": "#4285F4",
    "firebase": "#FFCA28",
    "heroku": "#430098",
    "netlify": "#00C7B7",
    "vercel": "#000000",
    "prometheus": "#E6522C",
    "grafana": "#F46800",
    "jenkins": "#D24939",
    "githubactions": "#2088FF",
    "gitlabci": "#FCA121",
    "circleci": "#343434",
    "vagrant": "#1563FF",
    "pulumi": "#8A3391",
    "helm": "#0F1689",
    "argocd": "#EF7B4D",
    "linux": "#FCC624",
    "ubuntu": "#E95420",
    "debian": "#A81D33",
    "arch": "#1793D1",
    "fedora": "#294172",
    "vim": "#019733",
    "neovim": "#57A143",
    "vscode": "#007ACC",
    "intellij": "#000000",
    "cmake": "#064F8C",
    "make": "#A42E00",
    "ninja": "#000000",
    "bazel": "#43A047",
    "meson": "#000000",
    "latex": "#008080",
    "markdown": "#000000",
    "yaml": "#CB171E",
    "json": "#000000",
    "xml": "#FF6600",
    "toml": "#9C4121",
    "regex": "#000000",
    "unity": "#000000",
    "unrealengine": "#0E1128",
    "godot": "#478CBF",
    "bevy": "#232326",
    "opengl": "#5586A4",
    "vulkan": "#AC162C",
    "directx": "#0078D7",
    "webgl": "#990000",
    "threejs": "#000000",
    "blender": "#E87D0D",
    "sdl": "#000000",
    "glfw": "#000000",
    "sfml": "#8CC445",
}


def make_banner_line(content: str) -> str:
    inner = f"*   {content}"
    pad = BANNER_WIDTH - len(inner) - 1
    return inner + " " * pad + "*"


def build_svg_banner(rel_path: str, purpose: str) -> str:
    lines = [
        "<!--",
        "*" * BANNER_WIDTH,
        make_banner_line(f"PROJECT : {PROJECT}"),
        make_banner_line(f"FILE    : {rel_path}"),
        make_banner_line(f"PURPOSE : {purpose}"),
        make_banner_line(f"AUTHOR  : {AUTHOR}"),
        make_banner_line(f"EMAIL   : {EMAIL}"),
        "*" * BANNER_WIDTH,
        "-->",
    ]
    return "\n".join(lines) + "\n"


def load_tech_icons() -> tuple[dict[str, str], str]:
    try:
        import yaml
        data = yaml.safe_load(TECH_YAML.read_text(encoding="utf-8"))
        return data.get("icons", {}), data.get("fallback", "")
    except Exception:
        return {}, ""


def is_badge_svg(svg_text: str) -> bool:
    """Reject horizontal Shields badges masquerading as square tech icons."""
    normalized = svg_text.lower()
    return (
        'shape-rendering="crispedges"' in normalized
        and "textlength=" in normalized
    )


def embed_local_icon(rel_path: str, fill_color: str | None = None) -> str:
    icon_path = ROOT / rel_path
    if not icon_path.exists():
        return ""
    svg_text = icon_path.read_text(encoding="utf-8")
    if is_badge_svg(svg_text):
        return ""
    # Embedded SVGs render more reliably without XML prologs or leading comments.
    svg_text = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg_text)
    svg_text = re.sub(r"^\s*<!--.*?-->\s*", "", svg_text, flags=re.DOTALL)
    if fill_color:
        svg_text = svg_text.replace('fill="currentColor"', f'fill="{fill_color}"')
        svg_text = svg_text.replace('fill="#000000"', f'fill="{fill_color}"')
    data = base64.b64encode(svg_text.encode("utf-8")).decode()
    return f"data:image/svg+xml;base64,{data}"


def get_icon_base64(tech_name: str, icons_map: dict[str, str]) -> str:
    tech_lower = tech_name.lower()
    icon_path = icons_map.get(tech_name, "")
    if not icon_path:
        for key, path in icons_map.items():
            if key.lower() == tech_lower:
                icon_path = path
                break
    if not icon_path or icon_path.startswith(("http://", "https://")):
        return ""
    return embed_local_icon(icon_path.removeprefix("./"))


def build_icon_element(tech: str, x: int, y: int, size: int, icons_map: dict[str, str]) -> str:
    href = get_icon_base64(tech, icons_map)
    if href:
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{href}"/>'
    color = TECH_COLORS.get(tech.lower(), "#8b949e")
    cx = x + size // 2
    cy = y + size // 2
    r = size // 2
    node_r = max(2, size // 12)
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        f'<path d="M{cx - 8} {cy + 6}L{cx} {cy - 7}L{cx + 8} {cy + 6}Z" '
        f'fill="none" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>'
        f'<circle cx="{cx - 8}" cy="{cy + 6}" r="{node_r}" fill="#ffffff"/>'
        f'<circle cx="{cx}" cy="{cy - 7}" r="{node_r}" fill="#ffffff"/>'
        f'<circle cx="{cx + 8}" cy="{cy + 6}" r="{node_r}" fill="#ffffff"/>'
    )


def build_ledger_items(
    techs: list[str],
    icons_map: dict[str, str],
    row_y: int,
    start_x: int,
) -> str:
    if not techs:
        return ""

    slot_width = (WIDTH - start_x) / len(techs)
    parts = []
    for index, tech in enumerate(techs):
        item_x = int(start_x + index * slot_width)
        icon = build_icon_element(tech, item_x, row_y + 17, ICON_SIZE, icons_map)
        label = html.escape(tech.upper())
        font_size = "8.5" if len(tech) > 10 else "9.5"
        parts.append(
            f'<g>{icon}'
            f'<text x="{item_x + 34}" y="{row_y + 35}" fill="currentColor" '
            f'font-size="{font_size}" font-family="{FONT}" font-weight="600" '
            f'letter-spacing="0.55">{label}</text></g>'
        )
    return "".join(parts)


def build_ledger_row(
    number: str,
    label: str,
    note: str,
    techs: list[str],
    icons_map: dict[str, str],
    theme: str,
    row_y: int,
    start_x: int,
) -> str:
    t = THEMES[theme]
    items = build_ledger_items(techs, icons_map, row_y, start_x)
    return (
        f'<g color="{t["text2"]}">'
        f'<line x1="0" y1="{row_y + 1}" x2="{WIDTH}" y2="{row_y + 1}" stroke="{t["border"]}"/>'
        f'<line x1="0" y1="{row_y + 1}" x2="48" y2="{row_y + 1}" stroke="{t["accent"]}" stroke-width="2"/>'
        f'<text x="0" y="{row_y + 36}" fill="{t["text2"]}" font-size="10" '
        f'font-family="{FONT}" letter-spacing="1.1">{number}</text>'
        f'<text x="42" y="{row_y + 30}" fill="{t["text1"]}" font-size="14" '
        f'font-family="{FONT}" font-weight="650">{html.escape(label)}</text>'
        f'<text x="42" y="{row_y + 47}" fill="{t["text2"]}" font-size="8" '
        f'font-family="{FONT}" letter-spacing="0.8">{html.escape(note)}</text>'
        f'{items}</g>'
    )


def build_svg(recent: list[str], loved: list[str], icons_map: dict[str, str], theme: str, lang: str = "es") -> str:
    recent_label = "EN USO" if lang == "es" else "IN USE"
    recent_note = "ACTIVIDAD RECIENTE" if lang == "es" else "RECENT ACTIVITY"
    loved_label = "BASE" if lang == "es" else "CORE"
    loved_note = "SIEMPRE A MANO" if lang == "es" else "ALWAYS CLOSE"
    rel_path = f"assets/stack/stack-{theme}-{lang}.svg"
    purpose = f"TECH STACK SVG ({theme.upper()}/{lang.upper()})"
    banner = build_svg_banner(rel_path, purpose)
    recent_row = build_ledger_row(
        "01", recent_label, recent_note, recent, icons_map, theme, 0, 205
    )
    loved_row = build_ledger_row(
        "02", loved_label, loved_note, loved, icons_map, theme, 64, 520
    )

    return banner + f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Tech Stack">
  {recent_row}
  {loved_row}
</svg>
"""


def generate_all(recent: list[str] | None = None, loved: list[str] | None = None, icons_map: dict[str, str] | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if icons_map is None:
        icons_map, _ = load_tech_icons()

    if recent is None or loved is None:
        if STACK_DATA.exists():
            data = json.loads(STACK_DATA.read_text(encoding="utf-8"))
            if recent is None:
                recent = data.get("recent", ["Python", "Docker", "Ansible"])
            if loved is None:
                loved = data.get("loved", ["Bash", "C", "Git"])
        else:
            if recent is None:
                recent = ["Python", "Docker", "Ansible"]
            if loved is None:
                loved = ["Bash", "C", "Git"]

    for theme in ("dark", "light"):
        for lang in ("es", "en"):
            svg = build_svg(recent, loved, icons_map, theme, lang)
            out = OUTPUT_DIR / f"stack-{theme}-{lang}.svg"
            out.write_text(svg, encoding="utf-8")

    print(f"Generated stack SVGs in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all()
