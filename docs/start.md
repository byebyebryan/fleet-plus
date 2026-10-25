# Choose the pieces you need

Fleet Plus brings together independently useful projects. Start with the workflow
you want, then follow the owning project's setup instructions.

| Your goal | Start with | Add when needed |
| --- | --- | --- |
| Read Codex session state locally | Agent Observer core/CLI | An explicitly hosted local service for cached clients |
| Build a dashboard or diagnostic utility | Agent Observer public reads | Mesh for cross-host delivery |
| Pick and open an SSH destination | SSH Plus and its Mesh authority | Your existing terminal and SSH configuration |
| Open/focus native Codex or Claude TUIs | Agent Plus | SSH Plus and the host helper for remote entry |
| Browse and manage tmux sessions | Tmux Plus and its exact Tmux Observer counterpart | Mesh/SSH for configured remote views |

## Start with Agent Observer

The simplest complete path is a local read on the machine that already runs your
Codex daemon. No fleet setup is required. Follow the
[first local read recipe](https://github.com/byebyebryan/agent-observer/blob/main/docs/getting-started.md)
to install the published, hash-pinned 0.7.0a10 core in its own Python environment.

Once that environment is active, choose the source and read:

```sh
agent-observer api
agent-observer list --host-scope workstation --provider codex \
  --codex-home "${CODEX_HOME:-$HOME/.codex}"
```

Use your own logical host label and the Codex home you intend to inspect. `api`
reports API 4 / snapshot-watch 6 without contacting a provider. `list` performs
the explicit native read and shows host, provider, phase, runtime, activity age,
turn/update information, identity and title. The linked recipe explains the table
and how to inspect coverage when rows are missing or unknown.

For multiple local readers, continue with the
[current Service 4 recipe](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/local-service.md).
It explains an existing endpoint or a separately owned cache, with exact commands
for reads, watches and shutdown. Local core/service use remains Mesh-free.

For working-set readers, use the current [working-set guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/working-set.md)
for membership, coverage and bounded read semantics.

For a new utility, use the [bounded public-read example](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/read-utilities.md).
It is a developer example using public facades, with explicit endpoint/identity
inputs and a bounded lifetime. It does not install a new dashboard or daemon.

## Add machines deliberately

For fleet reads, configure logical hosts/routes through the supported Host Mesh
authority and install the matching publisher on each source host. Check the
[compatibility guide](compatibility.md) and the owner's networking instructions.
Reachability, configured membership and current source evidence are distinct.
Follow the [directional example](architecture.md#directional-host-access) before
assuming one machine can read another.

## Open native agent tools

[Agent Plus](projects/agent-plus.md) discovers Codex/Claude environments and opens
or focuses its registered native TUI windows. The supported desktop is Linux,
Niri and dedicated Kitty windows. Codex and Claude manage conversations inside
those windows. Agent Plus needs neither Agent Observer nor Tmux.

For remote entry, SSH Plus supplies configured routes and the Agent Plus host
helper runs on the provider's host. Each native home/environment retains its
own identity; a Work label is not a cross-host or shared-history shortcut.

## Use tmux independently

[Tmux Plus](projects/tmux-plus.md) remains a generic tmux picker and CLI. Install
the exact Tmux Observer payload it pins: version strings alone do not satisfy
its complete module/hash guard. Tmux observation, explicit refresh, attach/focus
and guarded lifecycle actions have separate responsibilities.

## Existing managed installations

Use your deployment owner to update an existing managed setup. This site's
examples do not replace per-role manifests or install all six projects together.
The maintainer uses a private, operator-managed chezmoi setup with explicit
artifact pins and scoped application. Public release, installed selection,
native behavior and device acceptance remain separate evidence.
