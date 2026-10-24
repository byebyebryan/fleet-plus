# Tmux Observer

Passive default-server tmux observation, prepared local/fleet views and a separate
client for explicit actions. It supports generic tmux workflows independently
of native agent managers.

## Facts, views and actions

The host-local core reads tmux metadata. An explicitly started owner service
publishes cached facts. Prepared clients combine host and endpoint-local desktop
evidence; optional Mesh carries configured remote views.

Observation does not start a server, attach a client or create a session. Explicit
refresh uses its own bounded control path. A separate action client revalidates
the route and complete session identity before acting on consumer intent.

[Tmux Plus](tmux-plus.md) supplies browsing and presentation. Direct clients can
use the public native, prepared and action boundaries independently. Agent Plus
now opens native agent managers directly and has no Tmux dependency.

## Start using it

Python 3.11+ is required; native/service support targets Linux and the configured
default tmux server. Begin with the [read-interface examples](https://github.com/byebyebryan/tmux-observer#use-the-read-interfaces)
and [runtime architecture](https://github.com/byebyebryan/tmux-observer/blob/main/docs/reference/architecture.md).
Cached clients need the explicit owner/prepared services. Remote clients need
compatible Mesh/SSH configuration and the matching source publisher.

## Supported and experimental paths

Released Observer a9 and Tmux Plus a8 retain their independently selected Mesh a24
reader/bridge and normal full-view delivery. The optional complete-view feed pilot
is explicit and unselected; semantic delta is also unselected.

See [compatibility](../compatibility.md) for release provenance and independent
installed/graphical/physical evidence. Reduced relevance to agent runtimes does
not retire existing generic tmux observation or explicit actions.
