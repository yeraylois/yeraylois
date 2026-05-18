#!/usr/bin/env python3
#
# /*************************************************************
# *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
# *   FILE    : .github/scripts/update_stack.py               *
# *   PURPOSE : AUTO-DETECT AND UPDATE DYNAMIC TECH STACK     *
# *   AUTHOR  : Yeray Lois Sanchez                            *
# *   EMAIL   : yerayloissanchez@gmail.com                    *
# *************************************************************/
#

import os
import re
import sys
import json
import yaml
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
USERNAME = os.environ.get("GITHUB_USERNAME", "yeraylois")
REPO_NAME = os.environ.get("GITHUB_REPO", "yeraylois")
README_PATH = Path("README.md")
TECH_ICONS_PATH = Path("assets/tech_icons.yml")
STACK_JSON = Path("assets/stack/recent.json")

# FRAMEWORK DETECTION PATTERNS FROM REPO DESCRIPTIONS/TOPICS
FRAMEWORK_PATTERNS = {
    # EMBEDDED / IoT
    "Zephyr": [r"zephyr", r"zephyr.?rtos", r"zephyr.?project"],
    "FreeRTOS": [r"freertos", r"free.?rtos"],
    "ArduinoFramework": [r"arduino", r"arduino.?framework"],
    "PlatformIO": [r"platformio", r"platform.?io"],
    "ESP8266": [r"esp8266", r"esp.?8266"],
    "ESP32": [r"esp32", r"esp.?32"],
    "STM32": [r"stm32", r"stm.?32"],
    "RaspberryPi": [r"raspberry.?pi", r"rpi", r"raspi"],
    "BeagleBone": [r"beaglebone", r"beagle.?bone"],
    "Nordic": [r"nordic", r"nordic.?semi", r"nrf5"],
    "OpenOCD": [r"openocd", r"open.?ocd"],
    "Meshtastic": [r"meshtastic", r"mesh.?tastic"],
    "LoRa": [r"lora", r"lorawan"],
    "Protobuf": [r"protobuf", r"proto.?buf", r"protocol.?buffers"],
    "MQTT": [r"mqtt"],
    "Modbus": [r"modbus"],
    "CAN": [r"can.?bus", r"canbus"],
    "RTOS": [r"rtos", r"real.?time.?os"],
    "OpenSSL": [r"openssl"],
    "GnuTLS": [r"gnutls"],
    
    # DEVOPS / CLOUD
    "Docker": [r"docker", r"container"],
    "Kubernetes": [r"kubernetes", r"k8s"],
    "Terraform": [r"terraform", r"iac"],
    "Ansible": [r"ansible", r"playbook"],
    "Vagrant": [r"vagrant"],
    "Pulumi": [r"pulumi"],
    "Jenkins": [r"jenkins", r"ci/cd", r"cicd"],
    "GitHubActions": [r"github.?actions", r"gh.?actions"],
    "GitLabCI": [r"gitlab.?ci", r"gitlab"],
    "CircleCI": [r"circleci", r"circle.?ci"],
    "ArgoCD": [r"argocd", r"argo.?cd"],
    "Helm": [r"helm", r"helm.?chart"],
    "AWS": [r"aws", r"amazon.?web.?services", r"ec2", r"s3", r"lambda"],
    "Azure": [r"azure", r"microsoft.?azure"],
    "GCP": [r"gcp", r"google.?cloud", r"gcloud"],
    "Firebase": [r"firebase"],
    "Heroku": [r"heroku"],
    "Netlify": [r"netlify"],
    "Vercel": [r"vercel"],
    "Cloudflare": [r"cloudflare"],
    "Nginx": [r"nginx"],
    "Apache": [r"apache", r"httpd"],
    
    # FRAMEWORKS / WEB
    "NodeJS": [r"nodejs", r"node.?js"],
    "React": [r"react", r"reactjs"],
    "Angular": [r"angular", r"angularjs"],
    "Vue": [r"vue", r"vuejs", r"vue.?js"],
    "Svelte": [r"svelte"],
    "NextJS": [r"nextjs", r"next.?js"],
    "NuxtJS": [r"nuxtjs", r"nuxt.?js"],
    "Django": [r"django"],
    "Flask": [r"flask"],
    "FastAPI": [r"fastapi", r"fast.?api"],
    "Spring": [r"spring", r"spring.?boot"],
    "Express": [r"express", r"expressjs"],
    "NestJS": [r"nestjs", r"nest.?js"],
    "Laravel": [r"laravel"],
    "Rails": [r"rails", r"ruby.?on.?rails"],
    "Flutter": [r"flutter"],
    "Ionic": [r"ionic"],
    "ReactNative": [r"react.?native"],
    "Electron": [r"electron"],
    "Tauri": [r"tauri"],
    "Qt": [r"qt", r"qt5", r"qt6"],
    "GTK": [r"gtk"],
    "Blazor": [r"blazor"],
    "Phoenix": [r"phoenix"],
    "Rocket": [r"rocket.?rs", r"rocket.?rust"],
    "Actix": [r"actix"],
    
    # DATABASES
    "PostgreSQL": [r"postgresql", r"postgres"],
    "MySQL": [r"mysql", r"mariadb"],
    "MongoDB": [r"mongodb", r"mongo"],
    "Redis": [r"redis"],
    "SQLite": [r"sqlite"],
    "Cassandra": [r"cassandra"],
    "DynamoDB": [r"dynamodb", r"dynamo.?db"],
    "Neo4j": [r"neo4j"],
    "InfluxDB": [r"influxdb", r"influx"],
    "Elasticsearch": [r"elasticsearch", r"elastic"],
    "ClickHouse": [r"clickhouse"],
    "Supabase": [r"supabase"],
    "Prisma": [r"prisma"],
    
    # MONITORING
    "Prometheus": [r"prometheus"],
    "Grafana": [r"grafana"],
    "Datadog": [r"datadog"],
    "NewRelic": [r"new.?relic", r"newrelic"],
    "Sentry": [r"sentry"],
    "Jaeger": [r"jaeger"],
    "Loki": [r"loki"],
    "Zabbix": [r"zabbix"],
    "Nagios": [r"nagios"],
    "Wireshark": [r"wireshark"],
    
    # TESTING
    "Jest": [r"jest"],
    "Mocha": [r"mocha"],
    "Cypress": [r"cypress"],
    "Playwright": [r"playwright"],
    "Selenium": [r"selenium"],
    "Pytest": [r"pytest"],
    "unittest": [r"unittest"],
    "Catch2": [r"catch2"],
    "GoogleTest": [r"google.?test", r"gtest"],
    "JUnit": [r"junit"],
    
    # AI / ML
    "TensorFlow": [r"tensorflow"],
    "PyTorch": [r"pytorch", r"torch"],
    "Keras": [r"keras"],
    "ScikitLearn": [r"scikit", r"sklearn"],
    "Pandas": [r"pandas"],
    "NumPy": [r"numpy"],
    "Jupyter": [r"jupyter"],
    "OpenCV": [r"opencv"],
    "HuggingFace": [r"huggingface", r"hugging.?face"],
    "LangChain": [r"langchain"],
    "LlamaIndex": [r"llamaindex"],
    "Ollama": [r"ollama"],
    "OpenAI": [r"openai", r"gpt"],
    "Anthropic": [r"anthropic", r"claude"],
    "Kafka": [r"kafka", r"apache.?kafka"],
    "Spark": [r"spark", r"apache.?spark"],
    "Airflow": [r"airflow", r"apache.?airflow"],
    
    # TOOLS / OS
    "Git": [r"git"],
    "Bash": [r"bash", r"shell.?script"],
    "Zsh": [r"zsh"],
    "Vim": [r"vim"],
    "Neovim": [r"neovim", r"nvim"],
    "VSCode": [r"vscode", r"vs.?code"],
    "IntelliJ": [r"intellij"],
    "CLion": [r"clion"],
    "Eclipse": [r"eclipse"],
    "Linux": [r"linux"],
    "Ubuntu": [r"ubuntu"],
    "Debian": [r"debian"],
    "Arch": [r"arch", r"arch.?linux"],
    "Fedora": [r"fedora"],
    "Alpine": [r"alpine"],
    "Tmux": [r"tmux"],
    "Make": [r"make", r"makefile"],
    "CMake": [r"cmake"],
    "Ninja": [r"ninja"],
    "Bazel": [r"bazel"],
    "Meson": [r"meson"],
    "Conda": [r"conda"],
    
    # WEB / DESIGN
    "Bootstrap": [r"bootstrap"],
    "Tailwind": [r"tailwind", r"tailwind.?css"],
    "Sass": [r"sass", r"scss"],
    "Less": [r"less"],
    "MaterialUI": [r"material.?ui", r"mui"],
    "ChakraUI": [r"chakra"],
    "AntDesign": [r"ant.?design"],
    "Figma": [r"figma"],
    "Storybook": [r"storybook"],
    "Gatsby": [r"gatsby"],
    "Hugo": [r"hugo"],
    "Jekyll": [r"jekyll"],
    "Astro": [r"astro"],
    "GraphQL": [r"graphql"],
    "Apollo": [r"apollo"],
    "SocketIO": [r"socket\.io", r"socketio"],
    "WebRTC": [r"webrtc"],
    "PWA": [r"pwa", r"progressive.?web.?app"],
    "WordPress": [r"wordpress"],
    "Shopify": [r"shopify"],
    
    # SECURITY
    "WireGuard": [r"wireguard"],
    "OpenVPN": [r"openvpn"],
    "HashiCorpVault": [r"vault", r"hashicorp.?vault"],
    "Metasploit": [r"metasploit"],
    "Nmap": [r"nmap"],
    "Suricata": [r"suricata"],
    "Snort": [r"snort"],
    "Falco": [r"falco"],
    "Trivy": [r"trivy"],
    "Snyk": [r"snyk"],
    "SonarQube": [r"sonarqube", r"sonar.?qube"],
    
    # GAME DEV / GRAPHICS
    "Unity": [r"unity", r"unity3d"],
    "UnrealEngine": [r"unreal", r"unreal.?engine"],
    "Godot": [r"godot"],
    "Bevy": [r"bevy"],
    "OpenGL": [r"opengl"],
    "Vulkan": [r"vulkan"],
    "DirectX": [r"directx"],
    "WebGL": [r"webgl"],
    "ThreeJS": [r"three\.js", r"threejs"],
    "Blender": [r"blender"],
    "SDL": [r"sdl"],
    "GLFW": [r"glfw"],
    "SFML": [r"sfml"],
    
    # OTHERS
    "LaTeX": [r"latex", r"tex"],
    "Markdown": [r"markdown"],
    "JSON": [r"json"],
    "YAML": [r"yaml", r"yml"],
    "Regex": [r"regex", r"regexp"],
    "Graphviz": [r"graphviz"],
    "PlantUML": [r"plantuml"],
    "Doxygen": [r"doxygen"],
    "Sphinx": [r"sphinx"],
    "MkDocs": [r"mkdocs"],
    "GitBook": [r"gitbook"],
    "ReadTheDocs": [r"readthedocs", r"read.?the.?docs"],
}


def api_request(url):
    req = urllib.request.Request(url)
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "yeraylois-profile-stack-updater")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_all_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=pushed&direction=desc"
        data = api_request(url)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def detect_frameworks(repo):
    """Detect frameworks/tools from description, topics, and name."""
    text = " ".join([
        repo.get("description") or "",
        repo.get("name") or "",
        " ".join(repo.get("topics", []))
    ]).lower()
    
    detected = set()
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.add(framework)
                break
    return detected


def load_tech_icons():
    with open(TECH_ICONS_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data.get("icons", {}), data.get("fallback", "")


def get_recent_stack(repos, limit=6):
    """
    Returns list of (tech_name, last_push_date) ordered by recency.
    Priority: frameworks > languages.
    Most recent first (left side in the visual).
    """
    tech_entries = []  # LIST OF (tech_name, datetime, is_framework) FOR SORTING
    
    for repo in repos:
        pushed = repo.get("pushed_at")
        if not pushed:
            continue
        dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
        
        # FRAMEWORKS (HIGHER PRIORITY)
        frameworks = detect_frameworks(repo)
        for fw in frameworks:
            tech_entries.append((fw, dt, True))
        
        # LANGUAGE (LOWER PRIORITY)
        lang = repo.get("language")
        if lang and lang != "null":
            tech_entries.append((lang, dt, False))
    
    # SORT BY: IS_FRAMEWORK DESC, THEN DATETIME DESC
    # THIS ENSURES FRAMEWORKS APPEAR BEFORE LANGUAGES AT SAME TIMESTAMP
    tech_entries.sort(key=lambda x: (x[2], x[1]), reverse=True)
    
    # DEDUPLICATE, KEEPING MOST RECENT ENTRY FOR EACH TECH
    seen = set()
    unique_recent = []
    for tech, dt, is_fw in tech_entries:
        if tech not in seen:
            seen.add(tech)
            unique_recent.append((tech, dt))
        if len(unique_recent) >= limit * 2:
            break
    
    return unique_recent[:limit]


def create_issue_for_new_tech(new_techs, repo_name):
    if not new_techs:
        return
    
    body_lines = ["## 🆕 Nuevas tecnologías detectadas"]
    body_lines.append("")
    body_lines.append("Las siguientes tecnologías fueron detectadas en tus repositorios pero no tienen icono mapeado en `assets/tech_icons.yml`:")
    body_lines.append("")
    for tech in new_techs:
        body_lines.append(f"- **{tech}**")
    body_lines.append("")
    body_lines.append("### Acción requerida:")
    body_lines.append("1. Revisa si el nombre detectado es correcto")
    body_lines.append("2. Añade el icono correspondiente a `assets/tech_icons.yml`")
    body_lines.append("3. Cierra este issue cuando esté resuelto")
    body_lines.append("")
    body_lines.append(f"_Detectado en el repositorio: `{repo_name}`_")
    body_lines.append(f"_Fecha: {datetime.now().isoformat()}_")
    
    body = "\n".join(body_lines)
    title = f"🆕 Nueva tecnología detectada: {', '.join(new_techs)}"
    
    url = f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/issues"
    payload = json.dumps({"title": title, "body": body}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "yeraylois-profile-stack-updater")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Issue created: {resp.status}")
    except Exception as e:
        print(f"Failed to create issue: {e}", file=sys.stderr)


def main():
    print("=" * 60)
    print("  TECH STACK UPDATER")
    print(f"  User: {USERNAME}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 60)
    

    icons_map, fallback_url = load_tech_icons()
    print(f"\nLoaded {len(icons_map)} tech icons from {TECH_ICONS_PATH}")
    

    print("\nFetching repositories...")
    repos = fetch_all_repos()
    print(f"Found {len(repos)} repositories")
    

    recent_stack = get_recent_stack(repos, limit=6)
    print(f"\nRecent stack detected ({len(recent_stack)} items):")
    for tech, dt in recent_stack:
        print(f"  - {tech} (last used: {dt.strftime('%Y-%m-%d')})")
    

    unmapped = [tech for tech, _ in recent_stack if tech not in icons_map]
    if unmapped:
        print(f"\n⚠️  Unmapped technologies: {unmapped}")
        create_issue_for_new_tech(unmapped, REPO_NAME)
    else:
        print("\n✅ All technologies have icon mappings")
    

    # STATIC LOVED STACK
    loved_techs = ["Bash", "C", "Git"]

    print("\nSaving stack data...")
    STACK_JSON.parent.mkdir(parents=True, exist_ok=True)
    stack_data = {
        "recent": [tech for tech, _ in recent_stack],
        "loved": loved_techs,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(STACK_JSON, "w") as f:
        json.dump(stack_data, f, indent=2)

    print("\n✅ Stack data saved successfully!")
    print(f"   Recent stack: {len(stack_data['recent'])} technologies")
    print(f"   Loved stack: {len(stack_data['loved'])} technologies")


if __name__ == "__main__":
    main()
