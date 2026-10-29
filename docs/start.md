# Keep your sessions in view

Start with Agent Observer's terminal reader for quick checks, session
investigation and a persistent dashboard. Fleet Plus also includes independent
tools for host access, native TUI entry and generic tmux workflows.

## Set up the terminal reader

Requires Linux and Python 3.11+. Follow the owner's
[sessions CLI guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/sessions-cli.md#prerequisites)
to install the published reader pair in an isolated environment. For the
persistent TUI, follow the [dashboard guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/dashboard.md)
with its optional dependencies. Those guides own the current artifact hashes
and dependency pins.

**The reader needs existing working-set publishers/bridges.** Installing a reader
does not host a collector, start a provider or create a source. Check the owner's
[working-set prerequisites](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/working-set.md#bounded-inspection)
and arrange source hosting before continuing with reader setup.
A working-set bridge socket is distinct from the collector's Service 4 socket.

Next, [configure sources once](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/sessions-cli.md#configure-sources-once)
in your private `terminal.toml`. Each entry binds an existing host/home, Mesh
source, namespace and route/socket. Use the owning source's values; a friendly
home label cannot establish its identity. The file must be owned by your user,
regular, without a symlink, and mode 0600.

Check the configuration, then source health:

```sh
agent-observer sessions sources --configured
agent-observer sessions sources
```

The first command checks configuration without connecting. The second reads the
selected sources. Setup errors, unavailable sources and partial coverage remain
explicit, including when no sessions match.

## Check, investigate, keep watch

| What you need | Command |
| --- | --- |
| A quick overview, up to ten rows | `agent-observer` |
| All matching sessions and full IDs | `agent-observer sessions list` |
| Search admitted session metadata | `agent-observer sessions list --query renderer` |
| Inspect an exact session | `agent-observer sessions show FULL_THREAD_ID --host HOST --home HOME` |
| Inspect source health | `agent-observer sessions sources` |
| Versioned output for scripts | `agent-observer sessions list --format json` |
| A dashboard that stays open | `agent-observer dashboard` |

The dashboard reuses the CLI's source configuration. Search and filters narrow
the display while source health stays visible. Press `?` for keys and `q` to quit.
The JSON output is terminal interface 1; human tables are for reading.

For another host or home, follow [more hosts and homes](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/sessions-cli.md#more-hosts-and-homes).
Use existing directional routes and exact source bindings. A remote read grants
no reverse access. The [compatibility guide](compatibility.md) keeps reader,
producer and other consumer selections separate.

## Other ways into Fleet Plus

| Your goal | Start with |
| --- | --- |
| Pick and open an SSH destination | [SSH Plus](projects/ssh-plus.md) and its Mesh host authority |
| Open/focus native Codex or Claude TUIs | [Agent Plus](projects/agent-plus.md) |
| Browse and manage generic tmux sessions | [Tmux Plus](projects/tmux-plus.md) and its exact Tmux Observer counterpart |
| Inspect the owning local runtime | Observer's [first local read](https://github.com/byebyebryan/agent-observer/blob/main/docs/getting-started.md) |
| Build a read-only utility | Observer's [public-read example](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/read-utilities.md) |

Mesh and SSH Plus are independently useful. Agent Plus uses Host Mesh for
remote native entry and needs neither Observer nor Tmux. Native Codex/Claude
managers own conversations inside their windows. Tmux keeps its separate,
explicit session actions.

The diagnostic local core and Service 4 remain Mesh-free. The terminal sessions
reader uses the existing working-set Mesh bridges; these are separate read paths.
The [architecture guide](architecture.md) explains their responsibilities.

## Existing managed installations

Use your deployment owner to update a managed setup. This site's commands do not
replace role manifests or install all six projects together. The maintainer uses
a private operator-managed chezmoi setup; public onboarding needs only the
documented owner interfaces and your own explicit configuration.

Public release, installed selection, native behavior, resource qualification and
physical-device acceptance remain separate evidence.
