# Agent Observer

Read-only Codex state for dashboards, diagnostics and agent utilities. Observe
the native runtime where it lives, then choose a local or cross-host read path.

<!-- fleet-plus:dashboard -->
![RLCD agent dashboard renderer showing fictional conversations and activity states.](../../assets/dashboard.png)

*Production C renderer with fictional conversations and virtual time; this is a UI
preview, not physical panel footage. [Watch the rendered demo](../../assets/dashboard.gif)
or read the [media provenance](../../assets/provenance.json).*
<!-- /fleet-plus:dashboard -->

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

<!-- fleet-plus:read-path -->
**Codex runtime → Agent Observer → optional Mesh → your utility.**

| Read path | What it does |
| --- | --- |
| Local cached read | A separately running Observer service supplies facts to your utility. Reading does not start a daemon or renew native evidence. |
| Optional fleet delivery | Mesh carries already published observations over configured routes, preserving host outcomes, identities and evidence expiry. |
| Partial or expired evidence | Incomplete or unavailable evidence stays explicit. A missing row cannot prove an empty working set, idle work or removal. |
<!-- /fleet-plus:read-path -->

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

Follow [your first local Observer read](https://github.com/byebyebryan/agent-observer/blob/main/docs/getting-started.md):
install the published core in its own environment, choose an existing Codex home,
read local state and understand the table. Requires Linux, Python 3.11+ and your
existing native Codex runtime. Mesh, Rofi and tmux are unnecessary for this path.

For shared cached observations, use the [current Service 4 guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/local-service.md).
It covers an existing endpoint or a separately owned foreground publisher, cached
reads, watching and cleanup. Fleet delivery is an optional next step after the
local read works, with compatible Mesh, publishers and directional host routes.

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

The [compatibility guide](../compatibility.md) records the published working-set
pair, independent consumer versions and dated operational limits. Experimental
transport adoption retains its own explicit selection and qualification.
