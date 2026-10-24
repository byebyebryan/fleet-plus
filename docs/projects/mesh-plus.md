# Mesh Plus

Shared host authority and bounded delivery of cached Observer state. Producers
own native facts; Mesh owns how configured clients safely receive them.

## Two reusable responsibilities

The host authority models logical hosts, aliases, routes, revisions and route
health. SSH Plus exposes the supported Host Mesh process interface and SSH picker.
They use one selected authority; picker connection history remains with SSH Plus.

State delivery carries already published host-local observations over local IPC
and SSH. Pure Observer profiles preserve identities, coverage, freshness and
provenance. Readers handle source failure, expiry, changed incarnations and
gaps without converting missing evidence into current facts.

## Where it fits

- Agent Observer can use Mesh for optional cross-host read delivery.
- Tmux Observer supplies its own pure profile and cached publisher boundary.
- SSH Plus uses the shared authority implementation.
- Agent Plus uses Host Mesh routes through SSH Plus; it does not consume Mesh
  agent-state reads or require Observer.

Host access is directional. The [architecture guide](../architecture.md)
illustrates why one endpoint's roster does not authorize reverse access.

## Start using it

Python 3.11+ is required. Follow the [repository setup](https://github.com/byebyebryan/mesh-plus#install-and-inspect),
[Host Mesh boundary](https://github.com/byebyebryan/mesh-plus/blob/main/docs/guides/host-routing.md)
and [SDK reference](https://github.com/byebyebryan/mesh-plus/blob/main/docs/reference/sdk.md).
Domain reads require their compatible Observer package and configured publisher.
Mesh itself does not query a native provider or start a collector.

## Versions and experiments

Released a25 withdraws standalone Agent active-profile delivery while retaining
working-set, full Agent, Tmux and Host Mesh boundaries. Independent roles can
retain older reviewed Mesh versions; consult the [compatibility guide](../compatibility.md).

Semantic delta development remains dark and stopped at failed CPU/capacity gates.
The separately published complete-view feed and optional WSS transport require
explicit selection and their own adoption acceptance. Ordinary configured routes
retain complete-view delivery.
