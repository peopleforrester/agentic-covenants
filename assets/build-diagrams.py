#!/usr/bin/env python3
# ABOUTME: Generates the framework diagrams as SVG, one light and one dark per figure.
# ABOUTME: Hand-authored geometry, no drawing library, no runtime dependencies.
"""Build the Agentic Covenants diagrams.

Two figures, each emitted twice so a README can serve the right one per theme
via <picture> and prefers-color-scheme:

    three-layer-model    the thesis. Why the top layer fails and the lower two hold.
    six-matrices         the six matrices against the six NIST CSF 2.0 functions.

Why these are generated rather than drawn by hand in an editor: the labels
restate claims that appear in the prose, and a diagram that drifts from the
text is worse than no diagram. Generating from a single definition means a
palette or label change happens once, and `scripts/check.py` can assert the
committed SVGs still match what this script produces.

Why SVG rather than a raster: it projects at any size without softening, which
matters when the figure is on a conference screen, and it stays legible when a
reader zooms on a phone. It also diffs as text.

Usage:
    ./assets/build-diagrams.py            # write the SVGs
    ./assets/build-diagrams.py --check    # verify committed files are current
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent

W, H = 1600, 900  # 16:9


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    panel: str
    line: str
    ink: str
    dim: str
    faint: str
    l1: str
    l2: str
    l3: str
    accent: str
    danger: str


DARK = Theme("dark", "#0f1115", "#181d26", "#2b3444", "#e9eef5", "#9dabbd", "#6d7b8e",
             "#e0803a", "#3f9ad6", "#43b581", "#7aa2f7", "#e05252")
LIGHT = Theme("light", "#ffffff", "#f4f7fb", "#d3dde9", "#111820", "#4d5b6e", "#78879c",
              "#c26320", "#1f6fa8", "#22815a", "#2f5fd0", "#c0392b")

SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def text(x: float, y: float, s: str, size: float, fill: str, *,
         weight: str = "400", family: str = SANS, anchor: str = "start",
         spacing: str = "0", opacity: str = "1") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size:.1f}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{spacing}" opacity="{opacity}">{esc(s)}</text>')


def rect(x: float, y: float, w: float, h: float, *, fill: str = "none",
         stroke: str = "none", rx: float = 12, sw: float = 1.5,
         dash: str = "") -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_open(t: Theme, title: str, desc: str, w: int = W, h: int = H) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f'<rect width="{w}" height="{h}" fill="{t.bg}"/>\n'
    )


# --------------------------------------------------------------------------
# Figure 3: social preview card
# --------------------------------------------------------------------------
# GitHub renders this at roughly 600px wide in a feed and crops nothing, so the
# constraint is legibility at half size rather than density. Everything here is
# deliberately larger than it needs to be at 1:1.

SOCIAL_W, SOCIAL_H = 1280, 640


def fig_social(t: Theme) -> str:
    w, h = SOCIAL_W, SOCIAL_H
    out = [svg_open(t, "Agentic Covenants",
                    "Governance for autonomous agents, enforced by infrastructure "
                    "instead of by prompt.", w, h)]

    # Accent rule at the top, in the three layer colours, so the card carries
    # the framework's own visual key even at thumbnail size.
    for i, c in enumerate((t.l1, t.l2, t.l3)):
        out.append(f'<rect x="{i * w / 3:.1f}" y="0" width="{w / 3:.1f}" height="9" fill="{c}"/>')

    out.append(text(72, 132, "AGENTIC COVENANTS", 30, t.accent,
                    weight="700", family=MONO, spacing="3"))

    out.append(text(72, 236, "The layer you can talk to", 62, t.ink,
                    weight="700", spacing="-1.5"))
    out.append(text(72, 310, "is the layer that fails.", 62, t.dim,
                    weight="700", spacing="-1.5"))

    out.append(text(72, 374, "Governance for autonomous agents, enforced by "
                             "infrastructure instead of by prompt.", 24, t.dim))

    # Three compact layer chips restating the model.
    chips = [("IN-AGENT", "advisory", t.l1), ("CLIENT-SIDE", "deterministic", t.l2),
             ("SERVER-SIDE", "external", t.l3)]
    cw, cgap = 356, 20
    cy = 428
    for i, (name, verdict, c) in enumerate(chips):
        cx = 72 + i * (cw + cgap)
        out.append(rect(cx, cy, cw, 96, fill=t.panel, stroke=t.line, rx=12))
        out.append(f'<rect x="{cx}" y="{cy}" width="6" height="96" rx="3" fill="{c}"/>')
        out.append(text(cx + 26, cy + 42, name, 24, t.ink, weight="700", spacing="0.8"))
        out.append(text(cx + 26, cy + 72, verdict, 19, c, weight="600"))

    out.append(text(72, 592, "Six matrices · NIST CSF 2.0 · 93 cells · working artifacts",
                    22, t.faint))
    out.append(text(w - 72, 592, "agenticcovenants.com", 23, t.accent,
                    anchor="end", weight="700", family=MONO))
    out.append("</svg>\n")
    return "".join(out)


# --------------------------------------------------------------------------
# Figure 1: the three-layer model
# --------------------------------------------------------------------------

LAYERS = [
    dict(tag="L1", name="IN-AGENT", color="l1", verdict="ADVISORY",
         controls="System prompt · tool descriptions · refusals · “are you sure?”",
         why="Bypassable by language alone",
         porous=True),
    dict(tag="L2", name="CLIENT-SIDE", color="l2", verdict="DETERMINISTIC",
         controls="PreToolUse hooks · sandbox at launch · MCP allowlist · filesystem ACLs",
         why="Outside the model’s reasoning",
         porous=False),
    dict(tag="L3", name="SERVER-SIDE", color="l3", verdict="EXTERNAL",
         controls="RBAC · admission policy · IAM · branch protection · cosign",
         why="Outside the agent entirely",
         porous=False),
]


def fig_three_layer(t: Theme) -> str:
    out = [svg_open(
        t, "The layer you can talk to is the layer that fails",
        "Three enforcement layers. The in-agent layer is advisory and porous, so an "
        "agent's intent passes through it. The client-side and server-side layers are "
        "deterministic and hold, because they do not read the conversation.")]

    out.append(text(80, 96, "The layer you can talk to", 54, t.ink, weight="700", spacing="-1"))
    out.append(text(80, 156, "is the layer that fails.", 54, t.dim, weight="700", spacing="-1"))

    # Intent arrow entering from the top. Positioned to cross the barrier span
    # on the right, so the line is seen passing THROUGH the porous L1 barrier
    # and being halted by the solid L2 one. That crossing is the argument; an
    # arrow running down empty space beside the barriers makes no point.
    ax = 1100
    out.append(text(ax, 92, "agent decides to act", 20, t.danger, weight="600", anchor="middle"))
    out.append(f'<path d="M {ax} 108 L {ax} 196" stroke="{t.danger}" stroke-width="3" fill="none"/>')
    out.append(f'<path d="M {ax-8} 190 L {ax} 202 L {ax+8} 190 Z" fill="{t.danger}"/>')

    top, gap, bh = 210, 26, 178
    for i, layer in enumerate(LAYERS):
        y = top + i * (bh + gap)
        c = getattr(t, layer["color"])

        out.append(rect(80, y, 1440, bh, fill=t.panel, stroke=t.line, rx=14))
        # Colored spine identifies the layer without relying on text alone.
        out.append(f'<rect x="80" y="{y}" width="7" height="{bh}" rx="3.5" fill="{c}"/>')

        out.append(text(116, y + 46, layer["tag"], 20, c, weight="700", family=MONO))
        out.append(text(116, y + 92, layer["name"], 33, t.ink, weight="700", spacing="1.5"))
        out.append(text(116, y + 130, layer["controls"], 19, t.dim))
        out.append(text(116, y + 158, layer["why"], 18, t.faint, weight="600"))

        # Verdict pill, right aligned.
        pw = 232
        px = 1520 - 36 - pw
        out.append(rect(px, y + 30, pw, 40, fill="none", stroke=c, rx=20, sw=2))
        out.append(text(px + pw / 2, y + 57, layer["verdict"], 17, c,
                        weight="700", anchor="middle", spacing="1.2"))

        # The barrier: dashed and broken where the layer is porous, solid where it holds.
        # The barrier spans wider than the verdict pill so the intent line can
        # cross it without also striking through the pill above.
        by = y + bh - 30
        bx0, bx1 = 1000, 1520 - 36
        if layer["porous"]:
            out.append(f'<line x1="{bx0}" y1="{by}" x2="{bx1}" y2="{by}" stroke="{c}" '
                       f'stroke-width="4" stroke-dasharray="10 14" opacity="0.75"/>')
            out.append(text(bx1, by + 26, "porous", 15, t.faint, anchor="end", family=MONO))
        else:
            out.append(f'<line x1="{bx0}" y1="{by}" x2="{bx1}" y2="{by}" stroke="{c}" '
                       f'stroke-width="7"/>')
            out.append(text(bx1, by + 26, "holds", 15, t.faint, anchor="end", family=MONO))

        # The agent's intent passes through L1 unimpeded and terminates at L2.
        # Drawn as one continuous dashed run so the eye follows it to the stop
        # rather than losing it in the gap between panels.
        if i == 0:
            stop_y = top + (bh + gap) + bh - 30
            out.append(f'<path d="M {ax} {y} L {ax} {stop_y - 13}" stroke="{t.danger}" '
                       f'stroke-width="3" fill="none" stroke-dasharray="7 7"/>')
        elif i == 1:
            out.append(text(ax + 24, by - 16, "stopped here", 19, t.l2, weight="700"))
            out.append(f'<circle cx="{ax}" cy="{by}" r="12" fill="{t.bg}" stroke="{t.l2}" '
                       f'stroke-width="4"/>')

    out.append(text(80, 872, "Everything an agent can be told is advisory. "
                             "Constraints that hold live outside the model’s reasoning.",
                    21, t.dim))
    out.append(text(1520, 872, "agenticcovenants.com", 19, t.accent,
                    anchor="end", weight="600", family=MONO))
    out.append("</svg>\n")
    return "".join(out)


# --------------------------------------------------------------------------
# Figure 2: six matrices against the six CSF functions
# --------------------------------------------------------------------------

MATRICES = [
    ("GV", "Charter", "Govern", "authorizes", "Who allowed this\nagent to exist?"),
    ("ID", "Inventory", "Identify", "tracks", "What agents exist,\nand what do they touch?"),
    ("PR", "Covenants", "Protect", "binds", "What stops it\nfrom violating?"),
    ("DE", "Sentinels", "Detect", "watches", "How do we know\nit was breached?"),
    ("RS", "Interventions", "Respond", "stops", "How do I stop\nthe bleeding now?"),
    ("RC", "Restorations", "Recover", "rebuilds", "How do I get back\nto known-good?"),
]


def fig_six_matrices(t: Theme) -> str:
    out = [svg_open(
        t, "Six matrices mapped to the six NIST CSF 2.0 functions",
        "Charter authorizes, Inventory tracks, Covenants binds, Sentinels watches, "
        "Interventions stops, Restorations rebuilds. Recovery feeds back into prevention.")]

    out.append(text(80, 92, "Six matrices,", 50, t.ink, weight="700", spacing="-1"))
    out.append(text(80, 148, "one per NIST CSF 2.0 function", 50, t.dim, weight="700", spacing="-1"))
    out.append(text(1520, 100, "93 cells", 34, t.accent, anchor="end",
                    weight="700", family=MONO))
    out.append(text(1520, 136, "5 or 6 concerns × 3 layers, each", 18, t.faint, anchor="end"))

    n = len(MATRICES)
    m_left, m_right, top, bh = 80, 1520, 236, 372
    gap = 18
    bw = (m_right - m_left - gap * (n - 1)) / n
    # One colour per function. Govern and Identify previously shared the accent,
    # which read as though they were the same kind of thing.
    colors = ["#8b7ce8", t.accent, t.l3, t.l2, t.l1, t.danger]

    for i, (ab, name, fn, verb, q) in enumerate(MATRICES):
        x = m_left + i * (bw + gap)
        c = colors[i]
        out.append(rect(x, top, bw, bh, fill=t.panel, stroke=t.line, rx=14))
        out.append(f'<rect x="{x:.1f}" y="{top}" width="{bw:.1f}" height="6" rx="3" fill="{c}"/>')

        cx = x + bw / 2
        out.append(text(cx, top + 48, ab, 21, c, weight="700", anchor="middle", family=MONO))
        out.append(text(cx, top + 92, name, 25, t.ink, weight="700", anchor="middle"))
        out.append(text(cx, top + 120, fn, 17, t.faint, anchor="middle"))
        out.append(text(cx, top + 160, verb, 20, t.dim, anchor="middle",
                        weight="600"))

        for j, line in enumerate(q.split("\n")):
            out.append(text(cx, top + 206 + j * 23, line, 15, t.faint, anchor="middle"))

        # Every matrix has the same three-layer shape. Showing it in each card
        # says so without a sentence, and fills space that was otherwise dead.
        sy = top + bh - 92
        out.append(f'<line x1="{x + 22:.1f}" y1="{sy - 18}" x2="{x + bw - 22:.1f}" '
                   f'y2="{sy - 18}" stroke="{t.line}" stroke-width="1"/>')
        for k, (lc, ll) in enumerate([(t.l1, "in-agent"), (t.l2, "client"), (t.l3, "server")]):
            ly_ = sy + k * 22
            out.append(f'<rect x="{x + 24:.1f}" y="{ly_}" width="9" height="9" rx="2" fill="{lc}"/>')
            out.append(text(x + 42, ly_ + 9, ll, 13, t.faint))

        if i < n - 1:
            arrow_x = x + bw + gap / 2
            out.append(f'<path d="M {arrow_x - 6} {top + bh/2 - 9} L {arrow_x + 5} {top + bh/2} '
                       f'L {arrow_x - 6} {top + bh/2 + 9} Z" fill="{t.faint}"/>')

    # Feedback loop: recovery informs prevention.
    ly = top + bh + 88
    x_rc = m_left + (n - 1) * (bw + gap) + bw / 2
    x_pr = m_left + 2 * (bw + gap) + bw / 2
    out.append(f'<path d="M {x_rc} {top + bh} L {x_rc} {ly} L {x_pr} {ly} L {x_pr} {top + bh}" '
               f'stroke="{t.faint}" stroke-width="2" fill="none" stroke-dasharray="7 7"/>')
    out.append(f'<path d="M {x_pr - 7} {top + bh + 12} L {x_pr} {top + bh} '
               f'L {x_pr + 7} {top + bh + 12} Z" fill="{t.faint}"/>')
    out.append(text((x_rc + x_pr) / 2, ly - 14, "recovery feeds prevention", 17, t.faint,
                    anchor="middle"))

    out.append(text(80, 848, "Every populated cell carries a working artifact.", 20, t.dim))
    out.append(text(1520, 848, "agenticcovenants.com", 19, t.accent,
                    anchor="end", weight="600", family=MONO))
    out.append("</svg>\n")
    return "".join(out)


FIGURES = {
    "three-layer-model": fig_three_layer,
    "six-matrices": fig_six_matrices,
    "social-card": fig_social,
}


def render_all() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for name, fn in FIGURES.items():
        for theme in (LIGHT, DARK):
            files[HERE / f"{name}-{theme.name}.svg"] = fn(theme)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify committed SVGs match this script; write nothing")
    args = ap.parse_args()

    files = render_all()
    stale = []
    for path, content in files.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(path.name)
        else:
            path.write_text(content, encoding="utf-8")

    if args.check:
        for s in stale:
            print(f"  stale or missing: {s}", file=sys.stderr)
        print(f"{len(files)} diagram(s) checked, {len(stale)} stale")
        return 1 if stale else 0

    for path in sorted(files):
        print(f"wrote {path.relative_to(HERE.parent)} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
