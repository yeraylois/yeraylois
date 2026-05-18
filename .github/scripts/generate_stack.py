#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_stack.py             *
 *   PURPOSE : GENERATE SVG TECH STACK CARDS                 *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yerayloissanchez@gmail.com                    *
 *************************************************************/
"""

from __future__ import annotations

import base64
import html
import json
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets" / "stack"
ICONS_DIR = ROOT / "assets" / "icons" / "devicon"
TECH_YAML = ROOT / "assets" / "tech_icons.yml"
STACK_DATA = ROOT / "assets" / "stack" / "recent.json"

WIDTH = 840
HEIGHT = 140
ICON_SIZE = 34
ICON_GAP = 8

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


def embed_local_icon(rel_path: str, fill_color: str | None = None) -> str:
    icon_path = ROOT / rel_path
    if not icon_path.exists():
        return ""
    svg_text = icon_path.read_text(encoding="utf-8")
    # Embedded SVGs render more reliably without XML prologs or leading comments.
    svg_text = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg_text)
    svg_text = re.sub(r"^\s*<!--.*?-->\s*", "", svg_text, flags=re.DOTALL)
    if fill_color:
        svg_text = svg_text.replace('fill="currentColor"', f'fill="{fill_color}"')
        svg_text = svg_text.replace('fill="#000000"', f'fill="{fill_color}"')
    data = base64.b64encode(svg_text.encode("utf-8")).decode()
    return f"data:image/svg+xml;base64,{data}"


def fetch_and_cache_icon(tech_name: str, url: str) -> str:
    if not url:
        return ""
    safe_name = tech_name.lower().replace(" ", "").replace("/", "").replace("\\", "")
    local_path = ICONS_DIR / f"{safe_name}.svg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        context = None
        try:
            import certifi

            context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            context = None

        with urllib.request.urlopen(req, timeout=15, context=context) as resp:
            data = resp.read()
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        b64 = base64.b64encode(data).decode()
        if ".svg" in url.lower():
            return f"data:image/svg+xml;base64,{b64}"
        return f"data:image/png;base64,{b64}"
    except Exception:
        return ""


def get_icon_base64(tech_name: str, icons_map: dict[str, str]) -> str:
    tech_lower = tech_name.lower()
    local_path = f"assets/icons/devicon/{tech_lower}.svg"
    href = embed_local_icon(local_path)
    if href:
        return href
    url = icons_map.get(tech_name, "")
    if not url:
        for key, u in icons_map.items():
            if key.lower() == tech_lower:
                url = u
                break
    if url:
        href = fetch_and_cache_icon(tech_name, url)
        if href:
            return href
    return ""


def build_icon_element(tech: str, x: int, y: int, size: int, icons_map: dict[str, str]) -> str:
    href = get_icon_base64(tech, icons_map)
    if href:
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{href}"/>'
    color = TECH_COLORS.get(tech.lower(), "#8b949e")
    initial = html.escape(tech[:1].upper())
    cx = x + size // 2
    cy = y + size // 2
    r = size // 2
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        f'<text x="{cx}" y="{cy + 4}" fill="#ffffff" font-size="{size // 2 + 2}" '
        f'font-weight="700" font-family="{FONT}" text-anchor="middle">{initial}</text>'
    )


def build_icons_group(techs: list[str], icons_map: dict[str, str], center_x: int, y0: int) -> str:
    parts = []
    total_width = len(techs) * ICON_SIZE + (len(techs) - 1) * ICON_GAP
    x = center_x - total_width // 2
    for i, tech in enumerate(techs):
        icon_svg = build_icon_element(tech, x, y0, ICON_SIZE, icons_map)
        if icon_svg:
            parts.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{i * 0.15}s" fill="freeze"/>'
                f'{icon_svg}'
                f'</g>'
            )
        x += ICON_SIZE + ICON_GAP
    return "".join(parts)


def build_half(center_x: int, label: str, icon_href: str, techs: list[str], icons_map: dict[str, str], theme: str) -> str:
    t = THEMES[theme]
    label_text = html.escape(label)
    border = t["border"]
    accent = t["accent"]
    text1 = t["text1"]

    icon_size = 20
    icon_y = 18
    icon_img = ""
    if icon_href:
        icon_x = center_x - 70
        icon_img = f'<image x="{icon_x}" y="{icon_y}" width="{icon_size}" height="{icon_size}" href="{icon_href}"/>'

    label_svg = (
        f'<text x="{center_x}" y="36" fill="{text1}" '
        f'font-size="18" font-weight="700" font-family="{FONT}" text-anchor="middle">{label_text}</text>'
    )

    num_icons = len(techs)
    total_icons_width = num_icons * ICON_SIZE + (num_icons - 1) * ICON_GAP
    half_len = total_icons_width / 2
    line_y = 52
    line_svg = (
        f'<line x1="{center_x - half_len}" y1="{line_y}" x2="{center_x + half_len}" y2="{line_y}" '
        f'stroke="{accent}" stroke-width="1.5" stroke-linecap="round"/>'
        f'<line x1="{center_x - half_len}" y1="{line_y - 3}" x2="{center_x - half_len}" y2="{line_y + 3}" '
        f'stroke="{accent}" stroke-width="1.5" stroke-linecap="round"/>'
        f'<line x1="{center_x + half_len}" y1="{line_y - 3}" x2="{center_x + half_len}" y2="{line_y + 3}" '
        f'stroke="{accent}" stroke-width="1.5" stroke-linecap="round"/>'
    )

    icons_svg = build_icons_group(techs, icons_map, center_x, 68)

    return icon_img + label_svg + line_svg + icons_svg


def build_svg(recent: list[str], loved: list[str], icons_map: dict[str, str], theme: str, lang: str = "es") -> str:
    t = THEMES[theme]
    bg = t["bg"]
    border = t["border"]
    accent = t["accent"]

    recent_label_es = "𝐑𝐄𝐂𝐈𝐄𝐍𝐓𝐄"
    recent_label_en = "𝐑𝐄𝐂𝐄𝐍𝐓"
    loved_label_es = "𝐓𝐎𝐏"
    loved_label_en = "𝐋𝐎𝐕𝐄𝐃"

    recent_label = recent_label_es if lang == "es" else recent_label_en
    loved_label = loved_label_es if lang == "es" else loved_label_en
    rel_path = f"assets/stack/stack-{theme}-{lang}.svg"
    purpose = f"TECH STACK SVG ({theme.upper()}/{lang.upper()})"
    banner = build_svg_banner(rel_path, purpose)

    clip_id = "card-clip"
    defs = (
        f'<clipPath id="{clip_id}"><rect width="{WIDTH}" height="{HEIGHT}" rx="10"/></clipPath>'
    )

    card_bg = (
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" '
        f'fill="{bg}" stroke="{border}" stroke-width="1"/>'
    )

    left_bar = (
        f'<rect x="0" y="0" width="4" height="{HEIGHT}" fill="{accent}" clip-path="url(#{clip_id})"/>'
    )

    divider = (
        f'<line x1="{WIDTH // 2}" y1="20" x2="{WIDTH // 2}" y2="{HEIGHT - 20}" '
        f'stroke="{border}" stroke-width="1"/>'
    )

    text1 = t["text1"]
    clock_href = embed_local_icon("assets/icons/clock.svg", fill_color=text1)
    heart_href = embed_local_icon("assets/icons/heart.svg", fill_color=text1)

    left = build_half(210, recent_label, clock_href, recent, icons_map, theme)
    right = build_half(630, loved_label, heart_href, loved, icons_map, theme)

    return banner + f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Tech Stack">
  <defs>
    {defs}
  </defs>
  {card_bg}
  {left_bar}
  {divider}
  {left}
  {right}
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
