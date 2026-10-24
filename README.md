# Fleet Plus

Multi-host observation, SSH access and desktop tools, featuring Agent Observer.

Fleet Plus is the shared presentation and documentation home for six independent
projects. Agent Observer supplies read-only Codex observations; Mesh and SSH Plus
provide host access and delivery; Agent Plus opens native agent TUIs; the Tmux
pair serves generic tmux workflows. Choose the pieces your workflow needs.

**[Explore Fleet Plus →](https://dev.byebyebryan.com/fleet-plus/)**

[Choose your setup](docs/start.md) · [Architecture](docs/architecture.md) ·
[Compatibility and evidence](docs/compatibility.md)

Publication is recorded separately from local builds in the
[delivery evidence](docs/evidence/2026-10-23-presentation/README.md).

## Projects

| Project | Responsibility |
| --- | --- |
| [Agent Observer](https://github.com/byebyebryan/agent-observer) | Read-only Codex identities, runtime/activity facts, coverage and freshness |
| [Mesh Plus](https://github.com/byebyebryan/mesh-plus) | Host authority and bounded cached-state delivery |
| [SSH Plus](https://github.com/byebyebryan/rofi-ssh-plus) | SSH picker and public Host Mesh interface |
| [Agent Plus](https://github.com/byebyebryan/rofi-agent-plus) | Native Codex/Claude TUI discovery, launch and window focus |
| [Tmux Observer](https://github.com/byebyebryan/tmux-observer) | Passive tmux facts, prepared views and a separate action client |
| [Tmux Plus](https://github.com/byebyebryan/rofi-tmux-plus) | Tmux browsing and explicit session actions |

## Ownership

This repository owns the shared site, ecosystem explanations and cross-project
decisions. Component repositories retain installation/reference documentation,
contracts, implementation and releases. Chezmoi owns managed deployment selections.
The [project catalog](data/projects.json) records presentation metadata.

The site uses committed content and published media. Building it does not contact
native runtimes or discover a host fleet. Historical evidence stays with its owner.

## Development and publication

Requires Python 3.11+. The site builds offline after its two pinned Python
dependencies are installed:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B scripts/build.py --output /absolute/empty/fleet-plus-site
```

The builder refuses a nonempty destination or output inside this checkout. It
checks the ten routes, local links/anchors, canonical metadata, sitemap, exact
public file inventory and media hashes. Generated output remains untracked.

The owned headless-browser gate uses Node and the pinned development dependency:

```sh
npm ci
npx playwright install chromium
node scripts/check-browser.mjs /absolute/empty/fleet-plus-site
```

It serves only the built directory on a temporary loopback port and opens its own
headless Chromium. It checks four widths, observation/routing controls, motion,
keyboard navigation and no-JavaScript reading. No user browser or native runtime
is involved. `FLEET_SCREENSHOTS=/absolute/directory` optionally saves previews.

`.github/workflows/pages.yml` checks relevant source on pushes/PRs and publishes
main through GitHub Pages. Enable Pages with the GitHub Actions build type. The
project inherits the portfolio's domain; it needs no project CNAME or DNS change.
Verify the deployed HTML/assets against the reviewed build after publication.

## Updating content

Shared guides and product introductions live under `docs/`. Templates and
interactions live under `site/`. `data/projects.json` owns the public directory
and proposed GitHub descriptions/topics; changes to remote metadata are deliberate
owner actions, not side effects of a build. Add every public file to the explicit
build inventory. Media attribution and hashes live in `assets/provenance.json`;
retain the notices in `assets/LICENSES.txt`.

The [delivery plan](docs/delivery-plan.md) records first-edition scope and acceptance.
