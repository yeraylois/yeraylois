#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_cards.py             *
 *   PURPOSE : GENERATE SVG CARDS FOR PROJECTS & CONTACT     *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yerayloissanchez@gmail.com                    *
 *************************************************************/
"""

from __future__ import annotations

import base64
import html
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS_DIR = ROOT / ".github" / "cards"
OUTPUT_DIR = ROOT / "assets" / "cards"
ICONS_DIR = ROOT / "assets" / "icons"
TECH_YAML = ROOT / "assets" / "tech_icons.yml"

WIDTH = 840

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text1": "#e6edf3",
        "text2": "#7d8590",
        "accent": "#58a6ff",
        "arrow": "#7d8590",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d1d9e0",
        "text1": "#1f2328",
        "text2": "#656d76",
        "accent": "#0969da",
        "arrow": "#656d76",
    },
}

TECH_COLORS = {
    "ionic": "#3880FF",
    "android": "#3DDC84",
    "sqlite": "#0F80CC",
    "ansible": "#EE0000",
    "docker": "#2496ED",
    "python": "#3572A5",
    "angular": "#DD0031",
    "prometheus": "#E6522C",
    "grafana": "#F46800",
    "c": "#555555",
    "microchip": "#A22846",
    "embedded": "#F5822A",
    "zephyr": "#662d91",
    "githubactions": "#2088FF",
}

CONTACT_COLORS = {
    "email": "#EA4335",
    "linkedin": "#0A66C2",
    "github": "#181717",
}


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_tech_icons() -> tuple[dict[str, str], str]:
    try:
        import yaml
        data = yaml.safe_load(TECH_YAML.read_text(encoding="utf-8"))
        return data.get("icons", {}), data.get("fallback", "")
    except Exception:
        return {}, ""


def get_tech_icon_url(tech_id: str, icons_map: dict[str, str], fallback: str) -> str:
    # CASE-INSENSITIVE SEARCH
    tech_id_lower = tech_id.lower()
    for key, url in icons_map.items():
        if key.lower() == tech_id_lower:
            return url
    return fallback


def wrap_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def embed_icon(icon_name: str) -> str:
    icon_path = ICONS_DIR / icon_name
    if not icon_path.exists():
        return ""
    data = base64.b64encode(icon_path.read_bytes()).decode()
    return f"data:image/svg+xml;base64,{data}"


def fetch_icon_as_base64(url: str) -> str:
    """Download icon from URL and return as base64 data URI."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        b64 = base64.b64encode(data).decode()
        # DETECT MIME TYPE BY EXTENSION
        if ".svg" in url.lower():
            return f"data:image/svg+xml;base64,{b64}"
        elif ".png" in url.lower():
            return f"data:image/png;base64,{b64}"
        else:
            return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""


def embed_local_icon(rel_path: str) -> str:
    """Read local icon and return base64 data URI."""
    icon_path = ROOT / rel_path
    if not icon_path.exists():
        return ""
    data = base64.b64encode(icon_path.read_bytes()).decode()
    return f"data:image/svg+xml;base64,{data}"


def build_tech_icon_svg(tech_id: str, x: int, y: int, size: int, label: str) -> str:
    """Build robust tech icon: embed everything as base64 so GitHub renders it."""
    tech_id_lower = tech_id.lower()
    color = TECH_COLORS.get(tech_id_lower, "#8b949e")

    # LOCAL OVERRIDES (ALREADY BASE64)
    if tech_id_lower == "zephyr":
        href = embed_local_icon("assets/icons/zephyr.svg")
        if href:
            return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{href}"/>'
    elif tech_id_lower == "githubactions":
        href = embed_local_icon("assets/icons/github.svg")
        if href:
            return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{href}"/>'

    # DEVICON LOCAL FILES
    devicon_map = {
        "ansible": "assets/icons/devicon/ansible.svg",
        "docker": "assets/icons/devicon/docker.svg",
        "python": "assets/icons/devicon/python.svg",
        "angular": "assets/icons/devicon/angular.svg",
        "c": "assets/icons/devicon/c.svg",
    }
    if tech_id_lower in devicon_map:
        href = embed_local_icon(devicon_map[tech_id_lower])
        if href:
            return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{href}"/>'

    # FALLBACK: COLORED CIRCLE WITH INITIAL
    initial = html.escape(label[:1].upper())
    cx = x + size // 2
    cy = y + size // 2
    r = size // 2
    text_fill = "#ffffff"
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        f'<text x="{cx}" y="{cy + 4}" fill="{text_fill}" font-size="{size // 2 + 2}" '
        f'font-weight="700" font-family="{FONT}" text-anchor="middle">{initial}</text>'
    )


def build_project_card(project: dict, theme: str, lang: str = "es") -> str:
    t = THEMES[theme]
    name = html.escape(project["name"])
    desc_key = "description_es" if lang == "es" else "description_en"
    desc = html.escape(wrap_text(project.get(desc_key, ""), 70))
    tech_items = project.get("tech", [])

    # ACCENT COLOR FROM FIRST TECH
    primary_color = TECH_COLORS.get(
        tech_items[0]["id"].lower() if tech_items else "", "#8b949e"
    )

    # STACK ICONS (RIGHT SIDE)
    stack_parts = []
    stack_count = len(tech_items)
    icon_size = 22
    icon_gap = 6
    total_stack_width = stack_count * icon_size + (stack_count - 1) * icon_gap
    x_stack = WIDTH - 66 - total_stack_width
    for item in tech_items:
        tech_id = item.get("id", "").lower()
        label = item.get("label", tech_id)
        stack_parts.append(
            build_tech_icon_svg(tech_id, x_stack, 28, icon_size, label)
        )
        x_stack += icon_size + icon_gap
    stack_svg = "".join(stack_parts)

    # REPO ICON
    repo_icon_href = embed_icon("repo.svg")
    repo_svg = ""
    if repo_icon_href:
        repo_svg = (
            f'<image x="{WIDTH - 36}" y="26" width="26" height="26" '
            f'href="{repo_icon_href}"/>'
        )

    # SEPARATOR LINE BETWEEN STACK AND REPO ICON
    separator_svg = (
        f'<line x1="{WIDTH - 46}" y1="26" x2="{WIDTH - 46}" y2="54" '
        f'stroke="{t["border"]}" stroke-width="1"/>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="80" viewBox="0 0 {WIDTH} 80" role="img" aria-label="Project card: {name}">
  <defs>
    <clipPath id="card"><rect width="{WIDTH}" height="80" rx="10"/></clipPath>
  </defs>
  <rect width="{WIDTH}" height="80" rx="10" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="4" height="80" fill="{primary_color}" clip-path="url(#card)"/>
  <text x="20" y="33" fill="{t['text1']}" font-size="16" font-weight="700" font-family="{FONT}">{name}</text>
  <text x="20" y="55" fill="{t['text2']}" font-size="12.5" font-family="{FONT}">{desc}</text>
  {stack_svg}
  {separator_svg}
  {repo_svg}
</svg>
"""


def build_contact_card(contact: dict, theme: str, lang: str = "es") -> str:
    t = THEMES[theme]
    channel = html.escape(contact["channel"])
    handle = html.escape(contact["handle"])
    use_key = "use_es" if lang == "es" else "use_en"
    use_text = html.escape(contact.get(use_key, ""))
    color = CONTACT_COLORS.get(contact["id"], t["accent"])

    # ICON
    icon_href = embed_icon(contact["icon"])
    icon_svg = ""
    if icon_href:
        icon_svg = f'<image x="18" y="16" width="24" height="24" href="{icon_href}"/>'
    else:
        icon_svg = f'<circle cx="30" cy="28" r="12" fill="{color}"/>'

    # EXTERNAL LINK ICON
    link_href = embed_local_icon("assets/icons/link.svg")
    link_svg = ""
    if link_href:
        link_svg = (
            f'<image x="{WIDTH - 38}" y="15" width="26" height="26" '
            f'href="{link_href}"/>'
        )

    # SEPARATOR BETWEEN INFO AND USE
    separator_svg = (
        f'<line x1="580" y1="16" x2="580" y2="40" '
        f'stroke="{t["border"]}" stroke-width="1"/>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="56" viewBox="0 0 {WIDTH} 56" role="img" aria-label="Contact: {channel}">
  <defs>
    <clipPath id="card"><rect width="{WIDTH}" height="56" rx="10"/></clipPath>
  </defs>
  <rect width="{WIDTH}" height="56" rx="10" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="4" height="56" fill="{color}" clip-path="url(#card)"/>
  {icon_svg}
  <text x="52" y="28" fill="{t['text1']}" font-size="14" font-weight="600" font-family="{FONT}">{channel}</text>
  <text x="52" y="46" fill="{t['text2']}" font-size="11.5" font-family="{FONT_MONO}">{handle}</text>
  {separator_svg}
  <text x="600" y="32" fill="{t['text2']}" font-size="12" font-family="{FONT}">{use_text}</text>
  {link_svg}
</svg>
"""


def generate_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    projects = load_json(CARDS_DIR / "projects.json")
    for proj in projects:
        pid = proj["id"]
        for theme in ("dark", "light"):
            for lang in ("es", "en"):
                svg = build_project_card(proj, theme, lang)
                out = OUTPUT_DIR / f"project-{pid}-{theme}-{lang}.svg"
                out.write_text(svg, encoding="utf-8")

    contacts = load_json(CARDS_DIR / "contact.json")
    for contact in contacts:
        cid = contact["id"]
        for theme in ("dark", "light"):
            for lang in ("es", "en"):
                svg = build_contact_card(contact, theme, lang)
                out = OUTPUT_DIR / f"contact-{cid}-{theme}-{lang}.svg"
                out.write_text(svg, encoding="utf-8")

    print(f"Generated cards in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all()
