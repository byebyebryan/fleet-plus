# Agent Observer

Read-only Codex state for dashboards, diagnostics and agent utilities. Observe
the native runtime where it lives, then choose a local or cross-host read path.

{{DASHBOARD}}

## Useful facts, with their limits intact

Agent Observer supplies stable session identities, runtime/activity observations,
coverage and independently expiring evidence. A consumer can distinguish useful
current observations from partial, stale or unavailable state. It does not infer
that a missing session is idle or that a disconnected source has no work.

The [RLCD agent dashboard](https://github.com/byebyebryan/esp32-rlcd/tree/main/projects/agent-dashboard)
is an existing consumer. It chooses its own rows and presentation, consumes public
observations and owns the hardware protocol. Other read-only utilities can use
the same public boundaries without depending on that display.

## Follow an observation

{{READ_PATH}}

## Choose a read path

| Interface | Use |
| --- | --- |
| Direct host snapshot | Explicit inspection against the existing owning daemon |
| Local cached Service 4 | Read-only clients of an independently hosted collector/service |
| Working-set reads | Admitted active membership plus recent context; the reviewed default window is 72 hours |
| Full diagnostic feed | Fuller explicit inventories and diagnostic consumers |

Core/local hosting stays independent of Mesh. Optional Mesh adds configured
cross-host delivery. A window, terminal or tmux pane is not the authority for
native conversation runtime state. Codex's owning daemon supplies that evidence.

## Start using it

Python 3.11+ is required; native/service support targets Linux. Begin with the
[repository quick start](https://github.com/byebyebryan/agent-observer#start-from-a-checkout)
and [documentation directory](https://github.com/byebyebryan/agent-observer/blob/main/docs/README.md).
Cached reads need an explicit service; working-set/fleet reads additionally need
the compatible Mesh package, publisher and configured host routes.

For a utility, use the [bounded public-read example](https://github.com/byebyebryan/agent-observer/blob/main/docs/utility-read-guide.md)
and [API 4 contract](https://github.com/byebyebryan/agent-observer/blob/main/docs/api-v4.md).
The example supplies a content-free diagnostic summary; it is a developer example,
not a new daemon, wire contract or installed product.

## Current scope

Codex is the only implemented native observation adapter. Claude monitoring,
Observer writes and standalone active-only delivery are retired. Working-set
retains active membership; native provider tools own conversation control.

[Agent Plus](agent-plus.md) independently opens native Codex/Claude TUIs and
does not depend on Observer. [Codex Plus](https://dev.byebyebryan.com/codex-plus/)
provides separate native workflow augmentations. Neither relationship grants
Observer action authority.

The published a9/Mesh a25 working-set pair and independent consumer versions
are covered by the [compatibility guide](../compatibility.md). That dated record
includes Carbon's unresolved partial membership. Experimental delta/view-feed
adoption and additional physical/native qualification retain separate gates.
