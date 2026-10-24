# Fleet Plus

Multi-host observation, SSH access and desktop tools, featuring Agent Observer.

Fleet Plus is the shared presentation and documentation home for six independent
projects. Agent Observer supplies read-only Codex observations; Mesh and SSH Plus
provide host access and delivery; Agent Plus opens native agent TUIs; the Tmux
pair serves generic tmux workflows. Choose the pieces your workflow needs.

The first site edition is being prepared at
`https://dev.byebyebryan.com/fleet-plus/`. Publication is recorded separately
from local builds in [the delivery plan](docs/delivery-plan.md).

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

See [the delivery plan](docs/delivery-plan.md) for the first-edition scope and
acceptance checkpoints. Build instructions will be added with the static builder.
Source history records reviewable checkpoints; the site is published through
GitHub Pages after its local checks pass.
