#!/usr/bin/env python3
# ABOUTME: Static site generator for agenticcovenants.com. Reads the root YAML in
# ABOUTME: place and emits deep-linkable HTML with no runtime dependencies.
"""Build the Agentic Covenants presentation site.

Design constraints, and why they are what they are:

  * **No runtime dependencies, and no package manifest.** The repository
    advertises zero dependencies and CLAUDE.md states it has no build and no
    dependency tree so Dependabot has nothing to scan. A Node toolchain would
    make both false. The output here is plain HTML, one stylesheet, and a few
    lines of vanilla JS, so the claim stays true and the published artifact has
    no supply chain of its own. For a framework whose fifth concern is supply
    chain, that is the consistent choice rather than merely a convenient one.

  * **The YAML is read in place.** Content is never duplicated or forked. The
    six matrix files at the repository root remain the single source of truth,
    and the markdown essays remain the canonical readable form.

  * **Every cell is a real page at a real path**, not a hash route, so a cell
    can be deep-linked from a slide, a letter, or an issue and will still
    resolve years later without JavaScript running.

Usage:
    ./site/build.py                 # build into site/dist/
    ./site/build.py --out <dir>     # build elsewhere
    ./site/build.py --check         # verify inputs and report, writing nothing
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required to build the site: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
DOMAIN = "https://agenticcovenants.com"

# Extensions rendered inline as artifact source. Anything else is linked only.
RENDERABLE = {
    ".yaml", ".yml", ".json", ".sh", ".py", ".tf", ".rego", ".toml",
    ".rules", ".bt", ".service", ".sb", ".md", "",
}
MAX_INLINE_BYTES = 60_000


@dataclass(frozen=True)
class Matrix:
    """One of the six matrices, and how it presents."""

    slug: str          # url segment, the CSF function
    yaml_name: str     # file at repo root
    path_key: str      # per-schema key naming the artifact directory
    function: str      # NIST CSF 2.0 function
    abbrev: str
    verb: str
    order: int


MATRICES = [
    Matrix("govern", "charter", "charter_path", "Govern", "GV", "authorizes", 1),
    Matrix("identify", "inventory", "inventory_path", "Identify", "ID", "tracks", 2),
    Matrix("protect", "matrix", "controls_path", "Protect", "PR", "binds", 3),
    Matrix("detect", "sentinels", "sentinels_path", "Detect", "DE", "watches", 4),
    Matrix("respond", "interventions", "interventions_path", "Respond", "RS", "stops", 5),
    Matrix("recover", "restorations", "restorations_path", "Recover", "RC", "rebuilds", 6),
]

LAYER_ORDER = ["in-agent", "client-side", "server-side"]
LAYER_STRENGTH = {
    "in-agent": ("advisory", "Bypassable by language alone"),
    "client-side": ("deterministic", "Outside the model's reasoning"),
    "server-side": ("external", "Outside the agent entirely"),
}


def esc(text: object) -> str:
    return html.escape(str(text if text is not None else ""), quote=True)


def load(m: Matrix) -> dict:
    with (REPO / f"{m.yaml_name}.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def layer_of(cell: dict) -> str:
    """Return the cell's layer, normalizing the per-matrix layer vocabulary.

    Charter and Inventory name their layers differently (`self-declared`,
    `agent`, and so on). Mapping them onto the canonical three keeps the
    navigation identical across all six matrices, which is the whole point of
    the framework having one shape.
    """
    raw = cell.get("layer", "")
    if raw in LAYER_ORDER:
        return raw
    return {
        "self-declared": "in-agent",
        "agent": "in-agent",
        "declared": "in-agent",
        "operator": "client-side",
        "platform": "server-side",
        "organizational": "server-side",
        "org": "server-side",
    }.get(raw, raw)


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

def shell(title: str, description: str, body: str, depth: int, canonical: str,
          extra_class: str = "") -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{DOMAIN}{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{up}style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20100%20100'%3E%3Ctext%20y='.9em'%20font-size='90'%3E%F0%9F%9B%A1%3C/text%3E%3C/svg%3E">
</head>
<body class="{extra_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <a class="brand" href="{up}index.html"><strong>Agentic Covenants</strong></a>
  <nav aria-label="Matrices">
    {" ".join(f'<a href="{up}{m.slug}/index.html">{m.function}</a>' for m in MATRICES)}
  </nav>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <p><strong>Agentic Covenants.</strong> A practitioner framework for autonomous-agent governance.</p>
  <p>Content <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>.
     Code <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a>.
     Source on <a href="https://github.com/peopleforrester/agentic-covenants">GitHub</a>.</p>
  <p class="fine">Every artifact here is a template with intentional placeholders. Read it before you deploy it.</p>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Artifacts
# --------------------------------------------------------------------------

def artifacts_for(rel_dir: str) -> list[Path]:
    d = REPO / rel_dir
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_file() and p.name != "README.md")


def render_artifact(path: Path) -> str:
    rel = path.relative_to(REPO)
    gh = f"https://github.com/peopleforrester/agentic-covenants/blob/main/{rel}"
    try:
        size = path.stat().st_size
    except OSError:
        return ""

    head = (
        f'<figure class="artifact">'
        f'<figcaption><code>{esc(path.name)}</code>'
        f'<a class="src" href="{gh}">view on GitHub</a></figcaption>'
    )

    if path.suffix.lower() not in RENDERABLE or size > MAX_INLINE_BYTES:
        return head + f'<p class="note">{size:,} bytes. Too large to inline; open it on GitHub.</p></figure>'

    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return head + '<p class="note">Binary or unreadable; open it on GitHub.</p></figure>'

    return head + f'<pre><code>{esc(text)}</code></pre></figure>'


def read_cell_readme(rel_dir: str) -> str:
    """Return the cell README rendered as minimal HTML.

    A deliberately small markdown subset: headings, fenced code, tables, lists,
    bold, inline code, and links. Pulling in a markdown library for six
    constructs would cost the zero-dependency property this repo argues for.
    """
    p = REPO / rel_dir / "README.md"
    if not p.is_file():
        return ""
    return md_to_html(p.read_text(encoding="utf-8"))


def md_inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)

    def link(m: re.Match) -> str:
        text, href = m.group(1), m.group(2)
        if not href.startswith(("http://", "https://", "#")):
            href = ("https://github.com/peopleforrester/agentic-covenants/blob/main/"
                    + href.lstrip("./"))
        return f'<a href="{href}">{text}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)


def md_to_html(text: str) -> str:
    out: list[str] = []
    in_code = False
    in_list = False
    in_table = False

    def close_blocks() -> None:
        nonlocal in_list, in_table
        if in_list:
            out.append("</ul>"); in_list = False
        if in_table:
            out.append("</tbody></table></div>"); in_table = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            close_blocks()
            out.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(esc(line))
            continue

        if not stripped:
            close_blocks()
            continue

        if stripped.startswith("#"):
            close_blocks()
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            out.append(f"<h{level + 1}>{md_inline(stripped.lstrip('#').strip())}</h{level + 1}>")
            continue

        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells) and cells:
                continue  # separator row
            if not in_table:
                close_blocks()
                out.append('<div class="tw"><table><tbody>'); in_table = True
            row = "".join(f"<td>{md_inline(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            continue

        if re.match(r"^[-*+]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            if in_table:
                out.append("</tbody></table></div>"); in_table = False
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{md_inline(re.sub(r'^([-*+]|\\d+\\.)\\s+', '', stripped))}</li>")
            continue

        close_blocks()
        out.append(f"<p>{md_inline(stripped)}</p>")

    if in_code:
        out.append("</code></pre>")
    close_blocks()
    return "\n".join(out)


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def cell_page(m: Matrix, data: dict, cell: dict, concern: dict) -> tuple[str, str]:
    layer = layer_of(cell)
    strength, strength_note = LAYER_STRENGTH.get(layer, ("", ""))
    rel_dir = (cell.get(m.path_key) or "").rstrip("/")
    summary = str(cell.get("summary", "")).strip()

    empty = not summary or "empty by design" in summary.lower() or "no enforcement" in summary.lower()

    cites = cell.get("citations") or {}
    cite_rows = "".join(
        f"<tr><th>{esc(k.replace('_', ' ').upper())}</th><td>{esc(', '.join(map(str, v)) if isinstance(v, list) else v)}</td></tr>"
        for k, v in cites.items() if v
    )

    risks = cell.get("primary_bypasses") or cell.get("primary_failure_modes") or []
    risk_html = ""
    if risks:
        label = "Primary bypasses" if "primary_bypasses" in cell else "Primary failure modes"
        items = "".join(f"<li>{esc(r)}</li>" for r in risks)
        risk_html = (f'<section class="risks"><h2>{label}</h2>'
                     f'<p class="note">Documented, not hypothetical. A control whose bypass is '
                     f'undocumented is worse than no control, because somebody trusted it.</p>'
                     f'<ul>{items}</ul></section>')

    files = artifacts_for(rel_dir) if rel_dir else []
    if files:
        art = "".join(render_artifact(p) for p in files)
        art_html = f'<section class="artifacts"><h2>Artifacts ({len(files)})</h2>{art}</section>'
    elif empty:
        art_html = ('<section class="artifacts empty"><h2>Deliberately empty</h2>'
                    '<p>This cell has no artifact, and that is the argument rather than a gap. '
                    'At this layer, for this concern, nothing is enforced. Populating it with an '
                    'enforcement claim would invert what the framework is saying.</p></section>')
    else:
        art_html = ""

    readme = read_cell_readme(rel_dir) if rel_dir else ""
    readme_html = f'<section class="readme"><h2>Cell notes</h2>{readme}</section>' if readme else ""

    others = "".join(
        f'<a class="{"here" if l == layer else ""}" href="../{l}/index.html">{l.replace("-", " ")}</a>'
        for l in LAYER_ORDER
    )

    title = f"{concern['label']} at the {layer.replace('-', ' ')} layer | {m.function} | Agentic Covenants"
    body = f"""
<nav class="crumbs" aria-label="Breadcrumb">
  <a href="../../../index.html">Home</a> ›
  <a href="../../index.html">{esc(m.function)}</a> ›
  <span>{esc(concern['label'])}</span>
</nav>
<article class="cell">
  <p class="eyebrow">{esc(m.function)} ({esc(m.abbrev)}) · {esc(concern['label'])}</p>
  <h1>{esc(concern['label'])} <span class="at">at the</span> {esc(layer.replace('-', ' '))} <span class="at">layer</span></h1>
  <p class="strength strength-{esc(layer)}"><strong>{esc(strength)}</strong> · {esc(strength_note)}</p>
  <blockquote class="q">{esc(data.get('question', ''))}</blockquote>
  <nav class="layerswitch" aria-label="Layers">{others}</nav>
  <section class="summary"><h2>What this cell does</h2><p>{esc(summary) or "Not populated."}</p></section>
  {art_html}
  {readme_html}
  {risk_html}
  {f'<section class="cites"><h2>Crosswalk</h2><div class="tw"><table><tbody>{cite_rows}</tbody></table></div></section>' if cite_rows else ''}
  <p class="permalink">Cite this cell:
     <code>{DOMAIN}/{m.slug}/{esc(concern['id'])}/{esc(layer)}/</code></p>
</article>
"""
    return title, shell(title, summary[:180] or title, body, 3,
                        f"/{m.slug}/{concern['id']}/{layer}/")


def matrix_page(m: Matrix, data: dict) -> str:
    concerns = data.get("concerns", [])
    cells = {(c["concern"], layer_of(c)): c for c in data.get("cells", [])}

    rows = []
    for concern in concerns:
        tds = []
        for layer in LAYER_ORDER:
            cell = cells.get((concern["id"], layer))
            if not cell:
                tds.append('<td class="none"><span>not in this matrix</span></td>')
                continue
            summary = str(cell.get("summary", "")).strip()
            empty = "empty by design" in summary.lower() or "no enforcement" in summary.lower()
            n = len(artifacts_for((cell.get(m.path_key) or "").rstrip("/")))
            badge = ('<span class="badge empty">empty by design</span>' if empty
                     else f'<span class="badge">{n} artifact{"s" if n != 1 else ""}</span>')
            snippet = summary[:190] + ("…" if len(summary) > 190 else "")
            tds.append(
                f'<td><a href="{concern["id"]}/{layer}/index.html">'
                f'{badge}<span class="sn">{esc(snippet)}</span></a></td>'
            )
        rows.append(
            f'<tr><th scope="row"><a href="{concern["id"]}/{LAYER_ORDER[1]}/index.html">'
            f'{esc(concern["label"])}</a><span class="intent">{esc(concern.get("intent", ""))}</span></th>'
            + "".join(tds) + "</tr>"
        )

    title = f"{m.function} · {data.get('title', '')} | Agentic Covenants"
    body = f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> › <span>{esc(m.function)}</span></nav>
<h1>{esc(data.get('title', ''))}</h1>
<p class="eyebrow">NIST CSF 2.0 · {esc(m.function)} ({esc(m.abbrev)}) · {len(concerns)} concerns × 3 layers</p>
<blockquote class="q big">{esc(data.get('question', ''))}</blockquote>
<div class="tw">
<table class="matrix">
  <thead><tr><th>Concern</th>
    <th>In-agent <em>advisory</em></th>
    <th>Client-side <em>deterministic</em></th>
    <th>Server-side <em>external</em></th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>
<p class="note">Walk a row left to right and ask one question at each layer: if the agent decides to
violate this concern, what stops it <em>here</em>? All three populated is defense in depth. Only the
in-agent cell populated is an audit finding, because the model can be talked out of it.</p>
"""
    return shell(title, str(data.get("question", ""))[:180], body, 1, f"/{m.slug}/")


def index_page(loaded: dict[str, dict], totals: dict) -> str:
    flow = "".join(
        f'<a class="fn" href="{m.slug}/index.html">'
        f'<span class="ab">{esc(m.abbrev)}</span>'
        f'<strong>{esc(loaded[m.slug]["title"].replace("Agentic ", "").replace(" Matrix", ""))}</strong>'
        f'<span class="fnf">{esc(m.function)}</span>'
        f'<span class="verb">{esc(m.verb)}</span></a>'
        for m in MATRICES
    )

    body = f"""
<section class="hero">
  <h1>The layer you can talk to<br>is the layer that fails.</h1>
  <p class="lede">Governance for autonomous agents, enforced by infrastructure instead of by prompt.
  Six matrices mapped to the six NIST CSF 2.0 functions, {totals['cells']} cells, and a working
  artifact in every populated one.</p>
  <p class="cta"><a class="btn" href="protect/index.html">Start with Protect</a>
     <a class="btn ghost" href="https://github.com/peopleforrester/agentic-covenants">Source on GitHub</a></p>
</section>

<section class="opening">
  <h2>The thirty-second version</h2>
  <p>In July 2025, Replit's coding agent deleted a production database <strong>during an explicit
  action freeze</strong>, after being told eleven times not to act. It then fabricated roughly 4,000
  fake records and misrepresented whether a rollback was possible.</p>
  <p><strong>That agent was perfectly prompted.</strong> The instructions were clear, repeated, and
  unambiguous.</p>
  <p>Everything an agent can be <em>told</em> is advisory. It can be argued out of it, injected past
  it, or simply ignored. Constraints that hold are the ones that live outside the model's reasoning:
  in the hooks on the operator's machine, and the admission controllers on the target system.</p>
  <p class="evidence">Of organizations that reported a security incident involving an AI model or
  application, <strong>92% were missing role-based access, MFA, and similar controls</strong> on it.
  <span class="src">IBM Cost of a Data Breach 2026, 29 July 2026.</span> Those are not exotic
  controls. The same organizations apply them to their databases. They did not apply them to the
  agent.</p>
</section>

<section class="layers">
  <h2>Three layers, ordered by how hard they are to get around</h2>
  <div class="lgrid">
    <div class="l l1"><span class="tag">weakest</span><h3>In-agent</h3>
      <p>System prompts, tool descriptions, refusals, "are you sure?"</p>
      <p class="why">Bypassable by language alone.</p></div>
    <div class="l l2"><span class="tag">deterministic</span><h3>Client-side</h3>
      <p>PreToolUse hooks, sandbox at launch, MCP allowlists, filesystem ACLs.</p>
      <p class="why">Outside the model's reasoning.</p></div>
    <div class="l l3"><span class="tag">strongest</span><h3>Server-side</h3>
      <p>RBAC, admission policy, IAM, branch protection, cosign.</p>
      <p class="why">Outside the agent entirely.</p></div>
  </div>
</section>

<section class="functions">
  <h2>Six matrices, one per NIST CSF 2.0 function</h2>
  <div class="fgrid">{flow}</div>
  <p class="note">Charter authorizes, Inventory tracks, Covenants binds, Sentinels watches,
  Interventions stops, Restorations rebuilds. Recovery feeds back into prevention.</p>
</section>

<section class="scope">
  <h2>What this does not cover, stated plainly</h2>
  <p>Every control here is <strong>deterministic</strong>. A policy admits or denies. A whole class
  of agentic failure is not decidable by a policy engine, because the input is natural language and
  the failure is semantic: injection arriving inside a document, exfiltration where every individual
  action is authorized and only the aggregate is a leak, output that is confidently wrong rather
  than unauthorized.</p>
  <p>Those need scoring, which is probabilistic, with false positives, false negatives, and an
  evasion surface. The framework's argument is to use deterministic controls to bound probabilistic
  agents, so it cannot cover those by construction. That is a boundary rather than a flaw, and an
  unstated boundary reads as a claim to completeness.</p>
  <p><a href="protect/content-integrity/server-side/index.html">Content integrity</a> is where the
  two meet, and it is the one row whose server-side column is deliberately weak.</p>
</section>

<section class="honest">
  <h2>Every control here can be bypassed</h2>
  <p>The coverage map publishes the tally rather than hiding it. Of the ecosystem incidents in the
  corpus: <strong>3 prevented, 5 bounded or partial, 6 not prevented, 1 out of scope.</strong>
  The not-prevented column is dominated by platform defects and trusted-component compromise,
  neither of which is closable by adding cells.</p>
  <p><a href="https://github.com/peopleforrester/agentic-covenants/blob/main/ASSURANCE.md">Read the coverage map</a> ·
     <a href="https://github.com/peopleforrester/agentic-covenants/blob/main/BYPASSES.md">Read the bypass corpus</a></p>
</section>
"""
    return shell(
        "Agentic Covenants",
        "Governance for autonomous agents, enforced by infrastructure instead of by prompt. "
        f"Six matrices mapped to NIST CSF 2.0, {totals['cells']} cells, working artifacts throughout.",
        body, 0, "/", extra_class="home",
    )


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build(out: Path, check_only: bool = False) -> int:
    loaded: dict[str, dict] = {}
    problems: list[str] = []
    total_cells = 0
    total_artifacts = 0

    for m in MATRICES:
        data = load(m)
        loaded[m.slug] = data
        cells = data.get("cells", [])
        concern_ids = {c["id"] for c in data.get("concerns", [])}
        total_cells += len(cells)
        for cell in cells:
            if cell["concern"] not in concern_ids:
                problems.append(f"{m.yaml_name}.yaml: cell references unknown concern {cell['concern']!r}")
            rel = (cell.get(m.path_key) or "").rstrip("/")
            if rel and not (REPO / rel).is_dir():
                problems.append(f"{m.yaml_name}.yaml: {m.path_key} does not exist: {rel}")
            total_artifacts += len(artifacts_for(rel)) if rel else 0

    print(f"matrices: {len(MATRICES)}  cells: {total_cells}  artifacts: {total_artifacts}")
    for p in problems:
        print(f"  PROBLEM {p}", file=sys.stderr)
    if check_only:
        return 1 if problems else 0
    if problems:
        print("refusing to build with unresolved problems", file=sys.stderr)
        return 1

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    (out / "style.css").write_text(STYLE, encoding="utf-8")
    # Pages serves this repo at a custom domain; CNAME must sit at the root.
    (out / "CNAME").write_text("agenticcovenants.com\n", encoding="utf-8")
    # Tell Pages not to run Jekyll over the output.
    (out / ".nojekyll").write_text("", encoding="utf-8")

    totals = {"cells": total_cells, "artifacts": total_artifacts}
    (out / "index.html").write_text(index_page(loaded, totals), encoding="utf-8")

    urls = ["/"]
    pages = 1
    for m in MATRICES:
        data = loaded[m.slug]
        mdir = out / m.slug
        mdir.mkdir(parents=True, exist_ok=True)
        (mdir / "index.html").write_text(matrix_page(m, data), encoding="utf-8")
        urls.append(f"/{m.slug}/")
        pages += 1

        by_id = {c["id"]: c for c in data.get("concerns", [])}
        for cell in data.get("cells", []):
            concern = by_id.get(cell["concern"])
            if not concern:
                continue
            layer = layer_of(cell)
            cdir = mdir / concern["id"] / layer
            cdir.mkdir(parents=True, exist_ok=True)
            _, page = cell_page(m, data, cell, concern)
            (cdir / "index.html").write_text(page, encoding="utf-8")
            urls.append(f"/{m.slug}/{concern['id']}/{layer}/")
            pages += 1

    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{DOMAIN}{u}</loc></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")

    print(f"wrote {pages} pages to {out}")
    return 0


STYLE = """/* Agentic Covenants. One stylesheet, no framework, no build step. */
:root{
  --bg:#0f1115; --panel:#161a21; --panel2:#1c212a; --line:#2a3140;
  --ink:#e7ecf3; --dim:#9aa7b8; --faint:#6b7889;
  --l1:#e0803a; --l2:#3f9ad6; --l3:#43b581; --accent:#7aa2f7; --warn:#e5c07b;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme:light){
  :root{--bg:#fbfcfd;--panel:#fff;--panel2:#f3f6fa;--line:#d8e0ea;--ink:#131820;
        --dim:#4d5a6b;--faint:#76839a;--accent:#2f5fd0;}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
     line-height:1.6;font-size:17px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:var(--accent);color:#fff;padding:8px;z-index:99}
a{color:var(--accent)}
main{max-width:1120px;margin:0 auto;padding:28px 20px 72px}
h1,h2,h3{line-height:1.2;letter-spacing:-.02em}
h1{font-size:clamp(1.7rem,4.4vw,2.6rem);margin:.2em 0 .5em}
h2{font-size:clamp(1.15rem,2.4vw,1.5rem);margin:2em 0 .6em}
code{font-family:var(--mono);font-size:.88em}
pre{background:var(--panel2);border:1px solid var(--line);border-radius:8px;
    padding:14px;overflow-x:auto;font-size:.82rem;line-height:1.5}
pre code{white-space:pre}
blockquote.q{border-left:3px solid var(--accent);margin:1em 0;padding:.4em 0 .4em 1em;
             color:var(--dim);font-style:italic}
blockquote.q.big{font-size:1.12rem}
.note{color:var(--dim);font-size:.94rem}
.fine{color:var(--faint);font-size:.85rem}
.eyebrow{color:var(--faint);text-transform:uppercase;letter-spacing:.09em;
         font-size:.74rem;font-weight:600;margin:0}

header.site,footer.site{max-width:1120px;margin:0 auto;padding:16px 20px;
  display:flex;gap:14px;align-items:center;flex-wrap:wrap}
header.site{border-bottom:1px solid var(--line)}
header.site .brand{color:var(--ink);text-decoration:none;font-size:1.02rem}
header.site nav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
header.site nav a{color:var(--dim);text-decoration:none;font-size:.85rem;
  padding:5px 9px;border-radius:6px}
header.site nav a:hover{background:var(--panel2);color:var(--ink)}
footer.site{border-top:1px solid var(--line);margin-top:40px;display:block;
  color:var(--dim);font-size:.9rem}
footer.site p{margin:.35em 0}

/* home */
.hero{padding:44px 0 8px;border-bottom:1px solid var(--line)}
.hero h1{font-size:clamp(2rem,6vw,3.5rem);margin:0 0 .35em}
.lede{font-size:clamp(1rem,2vw,1.18rem);color:var(--dim);max-width:62ch}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin:1.6em 0 2em}
.btn{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;
  padding:11px 18px;border-radius:8px;font-weight:600;font-size:.95rem}
.btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.opening p{max-width:70ch}
.evidence{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:8px;padding:14px 16px;max-width:70ch}
.evidence .src{color:var(--faint);font-size:.85rem;display:block;margin-top:.35em}

.lgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.l{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;
   border-top:3px solid var(--line)}
.l h3{margin:.25em 0 .4em}
.l p{margin:.3em 0;font-size:.93rem;color:var(--dim)}
.l .why{color:var(--ink);font-weight:600;font-size:.88rem}
.l1{border-top-color:var(--l1)} .l2{border-top-color:var(--l2)} .l3{border-top-color:var(--l3)}
.tag{font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;color:var(--faint);font-weight:700}

.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:12px}
.fn{display:block;background:var(--panel);border:1px solid var(--line);border-radius:10px;
    padding:14px;text-decoration:none;color:var(--ink)}
.fn:hover{border-color:var(--accent)}
.fn .ab{font-family:var(--mono);font-size:.72rem;color:var(--accent);font-weight:700}
.fn strong{display:block;margin:.25em 0 .1em;font-size:1.05rem}
.fn .fnf{display:block;color:var(--faint);font-size:.8rem}
.fn .verb{display:block;color:var(--dim);font-size:.85rem;margin-top:.3em;font-style:italic}

/* tables */
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1em 0}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
thead th{background:var(--panel2);font-size:.82rem;position:sticky;top:0}
thead th em{display:block;color:var(--faint);font-weight:400;font-style:normal;font-size:.76rem}
table.matrix{min-width:860px}
table.matrix th[scope=row]{background:var(--panel2);min-width:170px}
table.matrix th[scope=row] a{text-decoration:none}
.intent{display:block;color:var(--faint);font-weight:400;font-size:.8rem;margin-top:.3em}
table.matrix td{padding:0}
table.matrix td a{display:block;padding:10px 12px;text-decoration:none;color:var(--ink);height:100%}
table.matrix td a:hover{background:var(--panel2)}
td.none span{display:block;padding:10px 12px;color:var(--faint);font-size:.83rem}
.badge{display:inline-block;background:var(--panel2);border:1px solid var(--line);
  border-radius:999px;padding:1px 9px;font-size:.7rem;color:var(--dim);
  font-family:var(--mono);margin-bottom:.5em}
.badge.empty{border-color:var(--l1);color:var(--l1)}
.sn{display:block;color:var(--dim);font-size:.85rem;line-height:1.45}

/* cell */
.crumbs{color:var(--faint);font-size:.85rem;margin:0 0 1em}
.crumbs a{color:var(--dim)}
.cell h1 .at{color:var(--faint);font-weight:400}
.strength{display:inline-block;font-size:.82rem;padding:4px 11px;border-radius:999px;
  background:var(--panel);border:1px solid var(--line)}
.strength-in-agent{border-color:var(--l1)}
.strength-client-side{border-color:var(--l2)}
.strength-server-side{border-color:var(--l3)}
.layerswitch{display:flex;gap:6px;flex-wrap:wrap;margin:1.4em 0}
.layerswitch a{padding:7px 13px;border:1px solid var(--line);border-radius:8px;
  text-decoration:none;color:var(--dim);font-size:.88rem;text-transform:capitalize}
.layerswitch a.here{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.summary p{max-width:74ch}
.artifact{margin:0 0 18px;border:1px solid var(--line);border-radius:10px;overflow:hidden;
  background:var(--panel)}
.artifact figcaption{display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  padding:9px 13px;background:var(--panel2);border-bottom:1px solid var(--line);font-size:.85rem}
.artifact figcaption code{font-weight:600}
.artifact .src{margin-left:auto;font-size:.8rem}
.artifact pre{border:0;border-radius:0;margin:0;max-height:520px;overflow:auto}
.artifact .note{padding:12px 13px;margin:0}
.artifacts.empty{border:1px dashed var(--l1);border-radius:10px;padding:2px 16px 14px;
  background:var(--panel)}
.artifacts.empty h2{color:var(--l1)}
.readme{border-top:1px solid var(--line);margin-top:2em}
.readme table{font-size:.85rem}
.risks ul{max-width:74ch}
.permalink{margin-top:2.5em;padding-top:1em;border-top:1px solid var(--line);
  color:var(--dim);font-size:.88rem}
.permalink code{background:var(--panel2);padding:3px 7px;border-radius:5px;
  border:1px solid var(--line);word-break:break-all}
@media (max-width:640px){
  body{font-size:16px}
  main{padding:20px 15px 56px}
  header.site nav a{padding:4px 7px;font-size:.8rem}
  .artifact pre{font-size:.74rem}
}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "dist"))
    ap.add_argument("--check", action="store_true", help="verify inputs, write nothing")
    args = ap.parse_args()
    return build(Path(args.out), check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
