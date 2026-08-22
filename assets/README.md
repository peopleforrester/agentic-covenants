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

Each is emitted twice, light and dark, so the README and the site can serve the right one per theme with `<picture>` and `prefers-color-scheme`.

## Why generated rather than drawn

The labels restate claims that also appear in the prose. A diagram that has drifted from the text is the same failure as a README number that no longer matches the tree, and it is harder to catch because nobody diffs an image. Generating from one definition means a label or palette change happens once, and `scripts/check.py` fails when a committed SVG no longer matches its generator.

## Why SVG

It projects at any size without softening, which is what matters when the figure is on a conference screen, and it stays legible when a reader zooms on a phone. It also diffs as text, so a change to a diagram is reviewable in a pull request.

There is no drawing library and no runtime dependency. Geometry is hand-computed in `build-diagrams.py`.

## Rendering to raster

Nothing here needs it, but a social preview card does, and GitHub cannot generate that from an SVG:

```bash
uvx --from cairosvg cairosvg assets/three-layer-model-dark.svg \
    -o /tmp/hero.png --output-width 1600
```

Setting the repository's social preview image is a manual step in GitHub settings; it is not exposed through the API.
