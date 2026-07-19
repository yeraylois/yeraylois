#!/usr/bin/env python3
"""Vendor every tech icon so README generation never depends on remote images."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "assets" / "icons" / "catalog"
TECH_YAML = ROOT / "assets" / "tech_icons.yml"
MANIFEST = CATALOG / "sources.json"
SIMPLE_ICON_VERSIONS = ("v16", "v15", "v14", "v13", "v12", "v11", "v10", "v9")
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@{version}/icons/{slug}.svg"
DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/{slug}/{slug}-{variant}.svg"
ICONIFY = "https://api.iconify.design/{icon}.svg"
USER_AGENT = "yeraylois-profile-icon-vendor/1.0"

FILENAME_OVERRIDES = {
    "C++": "cpp",
    "C#": "csharp",
    "ASP.NET": "aspnet",
    "Objective-C": "objective-c",
}

SLUG_OVERRIDES = {
    "Assembly": "assemblyscript",
    "C++": "cplusplus",
    "C#": "sharp",
    "Objective-C": "apple",
    "ArduinoFramework": "arduino",
    "FreeRTOS": "amazon",
    "BeagleBone": "beagleboard",
    "OpenOCD": "opensourcehardware",
    "RTOS": "amazonecs",
    "CAN": "socketdotio",
    "Modbus": "modrinth",
    "Loki": "grafana",
    "Screen": "gnubash",
    "Make": "gnu",
    "Nvm": "nodedotjs",
    "Pyenv": "python",
    "GnuTLS": "gnuprivacyguard",
    "NLTK": "python",
    "Seaborn": "python",
    "Fish": "fishshell",
    "SonarQube": "sonarqubeserver",
    "DirectX": "microsoft",
    "Maya": "autodesk",
    "unittest": "python",
    "GoogleTest": "google",
    "JUnit": "junit5",
    "MkDocs": "materialformkdocs",
}

DEVICON_OVERRIDES = {
    "DynamoDB": "dynamodb",
    "Fish": "fish",
    "Matplotlib": "matplotlib",
    "OpenGL": "opengl",
    "Playwright": "playwright",
    "SDL": "sdl",
}

ICONIFY_OVERRIDES = {
    "Zabbix": "logos:zabbix",
    "Nagios": "selfhst:nagios",
    "Ninja": "catppuccin:ninja",
    "Meson": "material-icon-theme:meson",
    "Nmap": "file-icons:nmap",
    "OSQuery": "logos:osquery",
    "WebSocket": "logos:websocket",
    "Regex": "mdi:regex",
    "Graphviz": "vscode-icons:file-type-graphviz",
    "PlantUML": "vscode-icons:file-type-plantuml",
}


def safe_filename(name: str) -> str:
    if name in FILENAME_OVERRIDES:
        return FILENAME_OVERRIDES[name]
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value or "unknown"


def load_sources(icons: dict[str, str]) -> dict[str, str]:
    if MANIFEST.exists():
        saved = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return {
            name: saved.get(name, {}).get("original_source", source)
            for name, source in icons.items()
        }
    return icons


def shield_logo(source: str) -> str:
    query = urllib.parse.parse_qs(urllib.parse.urlparse(source).query)
    return query.get("logo", [""])[0]


def icon_color(source: str, name: str) -> str:
    path = urllib.parse.unquote(urllib.parse.urlparse(source).path)
    match = re.search(r"-([0-9a-fA-F]{6})(?:$|[-?])", path)
    if match:
        return f"#{match.group(1).lower()}"
    digest = hashlib.sha256(name.encode()).hexdigest()
    return f"#{digest[:6]}"


def candidate_urls(name: str, source: str) -> list[str]:
    urls: list[str] = []
    if source.startswith("http") and "img.shields.io" not in source:
        urls.append(source)

    logo = shield_logo(source)
    slugs = [SLUG_OVERRIDES.get(name, ""), logo, safe_filename(name).replace("-", "")]
    for slug in slugs:
        if slug:
            slug = urllib.parse.quote(slug.lower())
            for version in SIMPLE_ICON_VERSIONS:
                urls.append(SIMPLE_ICONS.format(version=version, slug=slug))

    devicon_slugs = [DEVICON_OVERRIDES.get(name, ""), safe_filename(name).replace("-", "")]
    for slug in devicon_slugs:
        if slug:
            for variant in ("original", "plain"):
                urls.append(DEVICON.format(slug=slug, variant=variant))

    if name in ICONIFY_OVERRIDES:
        urls.append(ICONIFY.format(icon=ICONIFY_OVERRIDES[name]))

    return list(dict.fromkeys(urls))


def fetch_svg(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(1_500_000)
    svg = data.decode("utf-8", errors="strict").strip()
    if "<svg" not in svg.lower():
        raise ValueError("response is not SVG")
    if "textLength=" in svg and "crispEdges" in svg:
        raise ValueError("response is a horizontal badge")
    return re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg)


def colorize_simple_icon(svg: str, color: str) -> str:
    if re.search(r"<svg\b[^>]*\bfill=", svg):
        return svg
    return re.sub(r"<svg\b", f'<svg fill="{color}"', svg, count=1)


def generated_fallback(name: str, color: str) -> str:
    seed = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    variant = seed % 4
    paths = (
        '<path d="M5 12h14M12 5v14"/><circle cx="12" cy="12" r="8"/>',
        '<path d="M4 17 12 4l8 13-8 3z"/><circle cx="12" cy="12" r="2"/>',
        '<path d="M5 7h14v10H5zM8 4v6m8-6v6M8 14v6m8-6v6"/>',
        '<path d="m4 12 5-7h6l5 7-5 7H9zM8 12h8"/>',
    )[variant]
    label = html.escape(name, quote=True)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'role="img" aria-label="{label}" fill="none" stroke="{color}" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{paths}</svg>"
    )


def resolve_icon(name: str, source: str) -> tuple[str, str, str]:
    legacy = ROOT / "assets" / "icons" / "devicon" / f"{name.lower()}.svg"
    if legacy.exists():
        return legacy.read_text(encoding="utf-8"), str(legacy.relative_to(ROOT)), "existing"

    color = icon_color(source, name)
    for url in candidate_urls(name, source):
        try:
            svg = fetch_svg(url)
            if "simple-icons" in url:
                svg = colorize_simple_icon(svg, color)
            return svg, url, "downloaded"
        except (OSError, UnicodeError, ValueError, urllib.error.URLError):
            continue

    return generated_fallback(name, color), "generated:geometric-fallback", "generated"


def rewrite_catalog_paths(paths: dict[str, str]) -> None:
    lines = TECH_YAML.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    current_name: str | None = None
    for line in lines:
        if line.startswith("fallback:"):
            output.append('fallback: "./assets/icons/catalog/fallback.svg"')
            continue
        match = re.match(r'^  (?:(?:"([^"]+)")|(?:\'([^\']+)\')|([^:#][^:]*)):', line)
        if match:
            current_name = next(group for group in match.groups() if group is not None).strip()
            if current_name in paths:
                yaml_key = f'"{current_name}"' if current_name in FILENAME_OVERRIDES else current_name
                output.append(f'  {yaml_key}: "{paths[current_name]}"')
                continue
        output.append(line)
    TECH_YAML.write_text("\n".join(output) + "\n", encoding="utf-8")


def main() -> None:
    data = yaml.safe_load(TECH_YAML.read_text(encoding="utf-8"))
    icons: dict[str, str] = data["icons"]
    sources = load_sources(icons)
    CATALOG.mkdir(parents=True, exist_ok=True)

    fallback = generated_fallback("Unknown technology", "#8b949e")
    (CATALOG / "fallback.svg").write_text(fallback + "\n", encoding="utf-8")

    results: dict[str, tuple[str, str, str]] = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(resolve_icon, name, sources.get(name, "")): name
            for name in icons
        }
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()

    paths: dict[str, str] = {}
    manifest: dict[str, dict[str, str]] = {}
    for name in icons:
        svg, resolved_source, resolution = results[name]
        filename = f"{safe_filename(name)}.svg"
        destination = CATALOG / filename
        destination.write_text(svg.rstrip() + "\n", encoding="utf-8")
        paths[name] = f"./assets/icons/catalog/{filename}"
        manifest[name] = {
            "file": paths[name],
            "original_source": sources.get(name, ""),
            "resolved_source": resolved_source,
            "resolution": resolution,
            "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        }

    rewrite_catalog_paths(paths)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    generated = [name for name, item in manifest.items() if item["resolution"] == "generated"]
    print(f"Vendored {len(manifest)} icons in {CATALOG}")
    print(f"Downloaded/existing: {len(manifest) - len(generated)}")
    print(f"Geometric fallbacks: {len(generated)}")
    if generated:
        print("Fallback names: " + ", ".join(generated))


if __name__ == "__main__":
    main()
