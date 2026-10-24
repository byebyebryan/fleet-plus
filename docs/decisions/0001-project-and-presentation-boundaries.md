# Shared presentation, independent projects

Accepted 2026-10-23 during the ecosystem review.

## Decision

Keep the six source repositories separate and add Fleet Plus as a shared site
and cross-project documentation owner. Agent Observer receives the strongest
showcase. The homepage represents the broader collection; each component has
its own direct public entry page and GitHub homepage link.

Agent Observer's usefulness does not make the other projects its subcomponents.
Mesh is reusable authority/delivery infrastructure, SSH Plus owns access and its
public facade, Agent Plus independently enters native managers, and the Tmux
pair retains generic workflows. Native providers own conversations.

## Content ownership

Fleet Plus owns shared orientation, relationship diagrams, setup-choice guidance,
dated compatibility pointers and cross-project decisions. Components retain
installation/reference docs, implementation, contracts, artifacts and acceptance.
Chezmoi retains managed role selections and operations. Devlog articles explain
dated decisions and results; the personal portfolio links into the current guides.

Historical receipts remain with their original owner at stable paths. Current
guides link forward without rewriting historical qualification as present support.
The site builds from committed content, with no runtime or fleet discovery.

## Revisit conditions

Consider source consolidation if routine changes repeatedly require coordinated
edits, release prerequisites block integration, or compatibility maintenance becomes
materially costly. A meta repo improves presentation but does not make cross-repo
changes atomic. A distinct product site can grow later when its audience/content
justify independent maintenance.
