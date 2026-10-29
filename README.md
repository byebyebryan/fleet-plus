# Fleet Plus

Keep your Codex sessions in view, locally and across machines.

Agent Observer gives you a quick terminal overview, commands for session
investigation and a dashboard that stays open. It reads configured working-set
sources while native Codex owns the conversations.

Fleet Plus is the shared presentation home for six independent projects. Mesh
and SSH Plus provide host access and delivery; Agent Plus opens native Codex/Claude
TUIs; the Tmux pair serves generic tmux workflows. Choose the pieces you need.

**[Explore Fleet Plus →](https://dev.byebyebryan.com/fleet-plus/)**

[Set up the terminal reader](docs/start.md) · [Architecture](docs/architecture.md) ·
[Compatibility and evidence](docs/compatibility.md)

The reader needs existing working-set publishers/bridges and a private
`terminal.toml` with explicit source bindings. Follow the owning
[CLI setup](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/sessions-cli.md)
and optional [dashboard setup](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/dashboard.md)
guides for installation, then use:

```sh
agent-observer
agent-observer sessions list
agent-observer dashboard
```

The [first-edition delivery evidence](docs/evidence/2026-10-23-presentation/README.md)
retains its original publication checkpoint, separately from local builds.

## Projects

| Project | Responsibility |
| --- | --- |
| [Agent Observer](https://github.com/byebyebryan/agent-observer) | Terminal CLI/dashboard and public reads for Codex session state, coverage and freshness |
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

Product Markdown includes ordinary images/text between `fleet-plus` enhancement
comments. GitHub readers see those static fallbacks; the site builder replaces
the marked sections with its accessible controls. Keep the fallback readable and
complete, and use only the reviewed enhancement names. The build validates the
fallback links and rejects missing, empty, duplicate or unknown markers.

### Recreate the terminal media

The terminal capture is an explicit networked recipe, separate from the offline
site build. It installs the pinned render dependencies, downloads and verifies
the released Observer/Mesh wheels, then runs the actual dashboard against only
the fictional cached-source fixture. The wide still and demo use native colors;
the compact still uses the released CLI's supported `--color never` mode. To
write the three reviewed files and their provenance entries into `assets/`:

```sh
bash scripts/capture-terminal-media.sh
```

For a private preview and receipt, choose an output directory and receipt path:

```sh
FLEET_CAPTURE_RECEIPT=/tmp/observer-terminal-capture.json \
  bash scripts/capture-terminal-media.sh /tmp/observer-terminal-preview
```

The capture script records the exact package wheels, fixture/dependency and
recipe hashes, terminal dimensions, color modes, font and rendering transforms.
It does not read configured user sources or discover live sessions.

The [delivery plan](docs/delivery-plan.md) records current scope and acceptance,
with a fixed link to the first-edition plan.
[Publication checks](https://github.com/byebyebryan/fleet-plus/actions/workflows/pages.yml)
remain separate from local previews.

The [onboarding review corrections](docs/evidence/2026-10-23-onboarding/README.md)
record current Service 4 guidance, readable Markdown fallbacks and their separately
verified source, browser and public-delivery evidence.
