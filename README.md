# CertStack

A global regulatory tracker for consumer electronics products, covering nine
jurisdictions: EU, UK, US, CN, KR, JP, SA, AE, ZA.

See [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) for scope and principles, and
[`DECISIONS.md`](DECISIONS.md) for the project's architectural decision log.

## Structure

- `data/` — schema (`schema.yml`), controlled vocabulary (`vocab.yml`), and
  the regulatory tracker dataset (`tracker.yml`)
- `content/` — bilingual articles and shared content snippets
- `site/` — static frontend (single HTML file + vanilla JS)
- `tools/garan/` — tag generator tool
- `monitor/` — regulatory source monitoring configuration
- `scripts/` — build and validation tooling (Python 3, stdlib + PyYAML only)

## Requirements

- Python 3
- PyYAML (`pip install PyYAML`)

## Usage

Validate the tracker dataset:

```sh
python3 scripts/validate.py
```

Build `site/data.json` from the tracker dataset:

```sh
python3 scripts/build.py
```

## Deployment

The `site/` directory is deployed as a static site to Cloudflare Pages.
