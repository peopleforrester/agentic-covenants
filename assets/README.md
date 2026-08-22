# assets

Framework diagrams, generated as SVG.

```bash
python3 assets/build-diagrams.py            # write the SVGs
python3 assets/build-diagrams.py --check    # verify the committed files are current
```

| Figure | What it argues |
|---|---|
| `three-layer-model` | The thesis. An agent's intent passes straight through the advisory in-agent layer and is halted at the deterministic client-side one |
| `six-matrices` | The six matrices against the six NIST CSF 2.0 functions, and that each has the same three-layer shape |
| `social-card` | The GitHub social preview. 1280x640 rather than 16:9, because that is what GitHub renders |

Each is emitted twice, light and dark, so the README and the site can serve the right one per theme with `<picture>` and `prefers-color-scheme`.

## Why generated rather than drawn

The labels restate claims that also appear in the prose. A diagram that has drifted from the text is the same failure as a README number that no longer matches the tree, and it is harder to catch because nobody diffs an image. Generating from one definition means a label or palette change happens once, and `scripts/check.py` fails when a committed SVG no longer matches its generator.

## Why SVG

It projects at any size without softening, which is what matters when the figure is on a conference screen, and it stays legible when a reader zooms on a phone. It also diffs as text, so a change to a diagram is reviewable in a pull request.

There is no drawing library and no runtime dependency. Geometry is hand-computed in `build-diagrams.py`.

## The social preview card

**The file is `assets/social-card.png`.** It is committed, so setting it needs no tooling.

GitHub cannot use an SVG here, and the image cannot be set through the API, so this is the one artifact in the repo that is a committed raster and the one step that has to be done by hand.

To set it:

1. Open <https://github.com/peopleforrester/agentic-covenants/settings>
2. Scroll to **Social preview**
3. **Edit** to **Upload an image...**
4. Choose `assets/social-card.png`

It meets GitHub's stated spec: 1280x640 (they recommend that exact size, minimum 640x320) and 59 KB against a 1 MB ceiling. Verified 2026-08-23.

Once set, the card is what renders when the repo is linked from Slack, LinkedIn, X, iMessage, or anywhere else that reads Open Graph tags. Without it those unfurls show a generic GitHub avatar tile.

## Rendering any figure to raster

```bash
uvx --from cairosvg cairosvg assets/social-card-dark.svg \
    -o assets/social-card.png --output-width 1280
```

That is the exact command that produced the committed PNG. Regenerate it after changing `fig_social`, since `--check` compares the SVGs and cannot see a stale raster.
