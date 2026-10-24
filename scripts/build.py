#!/usr/bin/env python3
"""Build and validate Fleet Plus from committed, offline content."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "data/projects.json").read_text())
SITE = CATALOG["site"]
BASE = urlsplit(SITE).path
PROJECTS = CATALOG["projects"]
GUIDES = {
    "start/": (
        "docs/start.md",
        "Choose the pieces your workflow needs, from local Codex reads to SSH access, native entry and generic tmux.",
    ),
    "architecture/": (
        "docs/architecture.md",
        "How Agent Observer, Mesh, SSH and the launchers fit together, with directional host access and clear ownership.",
    ),
    "compatibility/": (
        "docs/compatibility.md",
        "Dated release combinations, independent installed roles and evidence boundaries for the Fleet Plus projects.",
    ),
}
for project in PROJECTS:
    GUIDES[f"projects/{project['slug']}/"] = (
        f"docs/projects/{project['slug']}.md",
        project["description"],
    )
SOURCE_ROUTES = {source: route for route, (source, _) in GUIDES.items()}
ASSETS = {
    "style.css",
    "site.js",
    "dashboard.png",
    "dashboard.gif",
    "agent-plus.png",
    "provenance.json",
    "LICENSES.txt",
    "relationships.svg",
}


def check_catalog() -> None:
    slugs = [project["slug"] for project in PROJECTS]
    expected = {
        "agent-observer",
        "mesh-plus",
        "ssh-plus",
        "agent-plus",
        "tmux-observer",
        "tmux-plus",
    }
    if len(slugs) != 6 or set(slugs) != expected:
        raise ValueError("catalog must contain the six reviewed independent projects")
    if [p["slug"] for p in PROJECTS if p["featured"]] != ["agent-observer"]:
        raise ValueError("Agent Observer must be the sole featured project")
    for project in PROJECTS:
        if not project["topics"] or len(set(project["topics"])) != len(
            project["topics"]
        ):
            raise ValueError("missing/duplicate repository topics")


def link_for_source(source: str, target: str) -> str:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith(("#", "/")):
        return target
    resolved = posixpath.normpath(
        posixpath.join(posixpath.dirname(source), unquote(parsed.path))
    )
    if resolved in SOURCE_ROUTES:
        return (
            BASE
            + SOURCE_ROUTES[resolved]
            + ("#" + parsed.fragment if parsed.fragment else "")
        )
    if resolved.startswith("assets/") and resolved.removeprefix("assets/") in ASSETS:
        return BASE + resolved
    raise ValueError(f"{source}: unregistered relative link {target}")


def prepare_enhancements(text: str, source: str) -> tuple[str, dict[str, str]]:
    """Replace marked, validated Markdown fallbacks only during the site build."""
    names = {"dashboard", "read-path", "routes", "agent-picker"}
    slots: dict[str, str] = {}
    seen: set[str] = set()
    pattern = re.compile(
        r"^<!-- fleet-plus:([a-z-]+) -->\n(.*?)\n<!-- /fleet-plus:\1 -->$",
        re.MULTILINE | re.DOTALL,
    )

    def replace(match):
        name, fallback = match.groups()
        if name not in names:
            raise ValueError(f"{source}: unknown enhancement {name}")
        if name in seen:
            raise ValueError(f"{source}: duplicate enhancement {name}")
        visible = re.sub(r"<!--.*?-->", "", fallback, flags=re.DOTALL).strip()
        if not visible:
            raise ValueError(f"{source}: empty enhancement fallback {name}")
        for token in MarkdownIt().enable("table").parse(fallback):
            for child in token.children or []:
                if child.type == "link_open":
                    link_for_source(source, child.attrGet("href") or "")
                elif child.type == "image":
                    link_for_source(source, child.attrGet("src") or "")
        seen.add(name)
        slot = f"FLEET_PLUS_ENHANCEMENT_{len(slots)}"
        slots[slot] = name
        return slot

    if "{{" in text:
        raise ValueError(f"{source}: use readable Markdown instead of template tokens")
    prepared = pattern.sub(replace, text)
    if re.search(r"<!--\s*/?fleet-plus:", prepared):
        raise ValueError(f"{source}: unmatched enhancement marker")
    return prepared, slots


def markdown(source: str) -> str:
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    prepared, enhancements = prepare_enhancements((ROOT / source).read_text(), source)
    tokens = parser.parse(prepared)
    headings: Counter[str] = Counter()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            label = tokens[index + 1].content
            slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            headings[slug] += 1
            token.attrSet(
                "id", slug if headings[slug] == 1 else f"{slug}-{headings[slug]}"
            )
        if token.children:
            for child in token.children:
                if child.type == "image":
                    child.attrSet(
                        "src", link_for_source(source, child.attrGet("src") or "")
                    )
                if child.type == "link_open":
                    child.attrSet(
                        "href", link_for_source(source, child.attrGet("href") or "")
                    )
    parser.renderer.rules["table_open"] = lambda *_: (
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable reference table"><table>\n'
    )
    parser.renderer.rules["table_close"] = lambda *_: "</table></div>\n"
    original_image = parser.renderer.rules["image"]

    def image_rule(tokens, idx, options, env):
        rendered = original_image(tokens, idx, options, env)
        if tokens[idx].attrGet("src") == BASE + "assets/relationships.svg":
            return (
                '<span class="diagram-scroll" tabindex="0" role="region" aria-label="Scrollable project relationship diagram">'
                + rendered
                + "</span>"
            )
        return rendered

    parser.renderer.rules["image"] = image_rule
    body = parser.renderer.render(tokens, parser.options, {})
    body = body.replace("<p>", '<p class="lede">', 1)
    project = next(
        (p for p in PROJECTS if source == f"docs/projects/{p['slug']}.md"), None
    )
    if project:
        actions = f'<div class="actions"><a class="button" href="https://github.com/byebyebryan/{project["repo"]}#readme">Installation &amp; reference ↗</a><a class="small-link" href="https://github.com/byebyebryan/{project["repo"]}/releases">Releases ↗</a></div>'
        body = body.replace("</p>", "</p>" + actions, 1)
    replacements = {
        "routes": (ROOT / "site/routes.html").read_text(),
        "read-path": (ROOT / "site/read-path.html").read_text(),
        "dashboard": dashboard("observer-dashboard"),
        "agent-picker": f'<figure><img class="product-image" src="{BASE}assets/agent-plus.png" alt="Agent Plus Rofi picker with local and remote example environments and native TUI windows" loading="lazy"><figcaption>Actual Rofi rendering with sample data and a preview theme. No live sessions are shown; your Rofi theme controls its appearance.</figcaption></figure>',
    }
    for slot, name in enhancements.items():
        body = body.replace("<p>" + slot + "</p>", replacements[name])
    if "FLEET_PLUS_ENHANCEMENT_" in body:
        raise ValueError(f"unresolved presentation include in {source}")
    return body


def dashboard(identity: str) -> str:
    return f'''<figure>
<div class="device"><div class="device-label"><span>AGENT OBSERVER → RLCD</span><span>UI RENDER</span></div>
<img id="{identity}" src="{BASE}assets/dashboard.png" data-still="{BASE}assets/dashboard.png" data-motion="{BASE}assets/dashboard.gif" width="400" height="300" alt="RLCD agent dashboard production renderer showing fictional Codex conversations and activity states"></div>
<button class="media-toggle" type="button" data-media-toggle="{identity}" aria-pressed="false" hidden>Play rendered demo</button>
<figcaption>Production dashboard renderer with fictional conversations and virtual time. This is a UI preview, not physical panel footage. <a href="{BASE}assets/provenance.json">Media provenance</a>.</figcaption></figure>'''


def homepage() -> str:
    projects = "".join(
        f'''<article class="project-row"><p class="role">{escape(p["role"])}</p><h3><a href="{BASE}projects/{p["slug"]}/">{escape(p["name"])}</a></h3><p>{escape(p["description"])}</p><a class="small-link" href="https://github.com/byebyebryan/{p["repo"]}">Source on GitHub ↗</a></article>'''
        for p in PROJECTS
    )
    return f'''<section class="intro"><p class="eyebrow">Observation · host access · desktop tools</p>
<h1>Your machines.<br>Your native tools.<br>A clearer view.</h1>
<p class="lede">Fleet Plus brings together six small projects for observing Codex, reaching hosts and opening useful native tools. Choose the pieces that fit your workflow.</p>
<div class="actions"><a class="button" href="{BASE}start/">Find your starting point</a><a class="button secondary" href="#projects">Explore the projects</a></div></section>
<section class="feature" aria-labelledby="observer-feature"><div class="text"><p class="eyebrow">Featured project · Agent Observer</p>
<h2 id="observer-feature">See useful agent state.<br>Across machines.</h2>
<p>Read-only Codex observations for dashboards, diagnostics and the next utility you want to build. Native managers keep ownership of the work.</p>
<p>Session identity, runtime and activity, with coverage and freshness kept explicit.</p><a class="button" href="{BASE}projects/agent-observer/">Explore Agent Observer</a></div>{dashboard("hero-dashboard")}</section>
<section class="section" aria-labelledby="workflow-title"><div class="section-heading"><p class="eyebrow">Other ways in</p><h2 id="workflow-title">Start with the job at hand.</h2><p>Related tools, independently useful. Opening a native TUI does not require an observation stack.</p></div>
<div class="cards"><article class="card"><span class="number">01 / HOST ACCESS</span><h3>Reach the right machine.</h3><p>Pick SSH destinations and share explicit host routes. Keep directional access intentional.</p><a href="{BASE}projects/ssh-plus/">SSH Plus &amp; Mesh →</a></article>
<article class="card"><span class="number">02 / NATIVE ENTRY</span><h3>Open your native agent tools.</h3><p>Find Codex and Claude environments. Open or focus dedicated TUI windows across configured hosts.</p><a href="{BASE}projects/agent-plus/">Agent Plus →</a></article>
<article class="card"><span class="number">03 / TMUX</span><h3>Keep tmux useful.</h3><p>Browse sessions, attach to useful context and use explicit guarded actions through independent tmux tooling.</p><a href="{BASE}projects/tmux-plus/">The Tmux tools →</a></article></div></section>
<section class="section" aria-labelledby="relationships-title"><div class="section-heading"><p class="eyebrow">How it fits</p><h2 id="relationships-title">Clear responsibilities.<br>Useful connections.</h2><p>Observer owns native facts. Mesh owns host authority and delivery. SSH Plus supplies access. Each utility owns its own presentation and intent.</p><a href="{BASE}architecture/">Explore the relationships and directional routes →</a></div></section>
<section class="section" id="projects" aria-labelledby="projects-title"><p class="eyebrow">The collection</p><h2 id="projects-title">Six projects. Their own paths.</h2><div class="project-grid">{projects}</div></section>
<section class="related section" aria-labelledby="related-title"><h2 id="related-title">Around the native workflow.</h2><p><a href="https://dev.byebyebryan.com/codex-plus/">Codex Plus</a> adds workers, watches, peer coordination and browser reports. <a href="https://github.com/byebyebryan/esp32-rlcd/tree/main/projects/agent-dashboard">The RLCD dashboard</a> turns observations into a desk display. Both retain their own implementation and delivery owners.</p><p><a href="{BASE}compatibility/">Read the dated compatibility and acceptance guide →</a></p></section>'''


def shell(
    route: str, title: str, description: str, body: str, source: str | None = None
) -> str:
    canonical = SITE + route
    navigation = [
        ("", "Overview"),
        ("start/", "Get started"),
        ("architecture/", "Architecture"),
    ]
    nav = "".join(
        f'<a href="{BASE}{target}"'
        + (' aria-current="page"' if route == target else "")
        + f">{label}</a>"
        for target, label in navigation
    )
    nav += f'<a href="{BASE}#projects">Projects</a><a href="https://github.com/byebyebryan/fleet-plus">GitHub ↗</a>'
    if source:
        body = (
            f'<article class="article"><p class="eyebrow">Fleet Plus / '
            + ("Project guide" if route.startswith("projects/") else "Shared guide")
            + f'</p>{body}<div class="page-links"><a href="{BASE}start/">Choose your setup</a><a href="{BASE}compatibility/">Compatibility &amp; evidence</a><a href="https://github.com/byebyebryan/fleet-plus/blob/main/{source}">Markdown source ↗</a></div></article>'
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} — Fleet Plus</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:site_name" content="Fleet Plus"><meta property="og:title" content="{escape(title, quote=True)} — Fleet Plus"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}assets/dashboard.png"><meta property="og:image:alt" content="Dashboard UI renderer with fictional conversations; not physical footage"><meta name="theme-color" content="#f6f5ef">
<link rel="stylesheet" href="{BASE}assets/style.css"><script defer src="{BASE}assets/site.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-row"><a class="brand" href="{BASE}"><span class="brand-mark" aria-hidden="true"></span>Fleet Plus</a><nav aria-label="Main navigation">{nav}</nav></div></header>
<main class="wrap" id="main" tabindex="-1">{body}</main>
<footer class="site-footer"><div class="wrap footer-row"><span>Small tools. Native workflows. Independently maintained.</span><span><a href="{BASE}compatibility/">Compatibility</a> · <a href="https://dev.byebyebryan.com/">Bryan's projects</a> · <a href="https://github.com/byebyebryan/fleet-plus">Site source</a></span></div></footer></body></html>\n'''


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.counts: Counter[str] = Counter()
        self.canonicals: list[str] = []
        self.descriptions: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.counts[tag] += 1
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "meta" and attrs.get("name") == "description":
            self.descriptions.append(attrs.get("content", ""))
        if tag == "img" and not attrs.get("alt"):
            raise ValueError("image without alt text")


def validate(output: Path) -> dict:
    routes = ["", *GUIDES]
    pages = {route + "index.html": SITE + route for route in routes}
    allowed = {
        *pages,
        *("assets/" + name for name in ASSETS),
        ".nojekyll",
        "sitemap.xml",
    }
    actual = {
        p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()
    }
    if actual != allowed:
        raise ValueError(
            f"public file inventory mismatch: missing={allowed - actual}, extra={actual - allowed}"
        )
    parsed = {name: Page((output / name).read_text()) for name in pages}
    links = 0
    for name, page in parsed.items():
        if len(page.ids) != len(set(page.ids)):
            raise ValueError(f"{name}: duplicate IDs")
        if page.counts["main"] != 1 or page.counts["h1"] != 1:
            raise ValueError(f"{name}: expected one main and H1")
        if (
            page.canonicals != [pages[name]]
            or len(page.descriptions) != 1
            or not page.descriptions[0]
        ):
            raise ValueError(f"{name}: invalid canonical/description")
        for target in page.links:
            url = urlsplit(urljoin(pages[name], target))
            if url.netloc != urlsplit(SITE).netloc:
                continue
            if not url.path.startswith(BASE):
                continue
            relative = unquote(url.path[len(BASE) :])
            relative += "index.html" if relative.endswith("/") or not relative else ""
            if relative not in actual:
                raise ValueError(f"{name}: missing local target {target}")
            if (
                url.fragment
                and relative in parsed
                and unquote(url.fragment) not in parsed[relative].ids
            ):
                raise ValueError(f"{name}: missing local anchor {target}")
            links += 1
    sitemap = ET.fromstring((output / "sitemap.xml").read_text())
    if [x.text for x in sitemap.findall("{*}url/{*}loc")] != list(pages.values()):
        raise ValueError("sitemap differs from public routes")
    provenance = json.loads((output / "assets/provenance.json").read_text())
    for entry in provenance["media"]:
        path = output / "assets" / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"media hash mismatch: {path.name}")
    return {"pages": len(pages), "files": len(actual), "local_links": links}


def build(output: Path) -> dict:
    check_catalog()
    output = output.absolute()
    if output.is_symlink() or output.resolve().is_relative_to(ROOT):
        raise ValueError("build output must be outside the checkout and not a symlink")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("build output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    (output / "assets").mkdir()
    for name in ASSETS:
        source = (
            ROOT / ("site" if name in {"style.css", "site.js"} else "assets") / name
        )
        shutil.copyfile(source, output / "assets" / name)
    (output / "index.html").write_text(
        shell(
            "",
            "Observation, host access and desktop tools",
            "Multi-host observation, SSH access and desktop tools, featuring Agent Observer and independent native workflows.",
            homepage(),
        )
    )
    for route, (source, description) in GUIDES.items():
        body = markdown(source)
        title = (ROOT / source).read_text().splitlines()[0].removeprefix("# ")
        target = output / route / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(shell(route, title, description, body, source))
    (output / ".nojekyll").write_text("")
    urls = [SITE, *(SITE + route for route in GUIDES)]
    (output / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls)
        + "</urlset>\n"
    )
    return validate(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            validate(args.output) if args.validate_only else build(args.output),
            sort_keys=True,
        )
    )
