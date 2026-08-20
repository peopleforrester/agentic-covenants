# site

The presentation layer for [agenticcovenants.com](https://agenticcovenants.com). A second surface over the same source, not a fork of it.

```bash
python3 site/build.py            # build into site/dist/
python3 site/build.py --check    # validate inputs, write nothing
```

## What it reads

The six matrix YAML files at the repository root, **in place**. Content is never duplicated. The markdown essays (`MATRIX.md`, `SENTINELS_MATRIX.md`, and the rest) remain the canonical readable form; this renders the same data for a different reader.

If a cell is added to a YAML file, it appears on the site with no other change. If a `*_path` key points at a directory that does not exist, `--check` fails and refuses to build.

## Why there is no Node toolchain

The repository advertises zero dependencies, and `AGENTS.md` states it has no build and no dependency tree so Dependabot has nothing to scan. A Vite or TypeScript setup would make both false and give the published artifact a supply chain of its own.

For a framework whose fifth concern is supply chain, shipping a site with 200 transitive dependencies would be an argument against itself. The output here is plain HTML, one stylesheet, and no JavaScript at all.

The only build-time requirement is PyYAML, which `scripts/check.py` already uses. Nothing is required at runtime, by the reader or the server.

## Structure

Every cell is a real page at a real path, not a hash route:

```
/                                          the thesis
/protect/                                  a matrix
/protect/content-integrity/server-side/    a cell
```

That means a cell can be cited from a slide, a letter, or an issue and will still resolve without JavaScript running. Each cell page carries its own permalink for exactly that use.

## Deployment

Built locally and published to the `gh-pages` branch. No CI minutes are consumed.

```bash
python3 site/build.py
./site/deploy.sh
```

`CNAME` and `.nojekyll` are emitted by the generator, so the custom domain and the raw-file serving survive every rebuild.

## Output

`site/dist/` is generated and gitignored. It is the published artifact, not source. Do not edit it; edit the YAML or the generator.
