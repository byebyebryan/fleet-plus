# Compatibility and evidence

Use the role you need, then follow that component's current installation guide.
Versions are independent: a new terminal reader does not upgrade a producer,
native launcher, tmux client or hardware dashboard. Source, public release,
installed selection, native evidence, resource qualification and physical
acceptance are separate checkpoints.

## Current roles — 2026-10-29

| Role | Reviewed selection | Owner record |
| --- | --- | --- |
| Terminal sessions CLI and optional dashboard | Agent Observer **0.7.0a14** + Mesh **0.1.0a25** | [CLI setup](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/sessions-cli.md), [dashboard setup](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/dashboard.md) and [a14 provenance](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a14/provenance.json) |
| Collector and working-set publication | Agent Observer **0.7.0a11** + Mesh **0.1.0a25** | [a11 release](https://github.com/byebyebryan/agent-observer/releases/tag/v0.7.0a11), [provenance](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a11/provenance.json) and [operations](https://github.com/byebyebryan/agent-observer/blob/main/docs/maintenance/operations.md) |
| Native Codex/Claude entry | Agent Plus **0.15.0a17** | [a17 release](https://github.com/byebyebryan/rofi-agent-plus/releases/tag/v0.15.0a17) and [managed operations](https://github.com/byebyebryan/rofi-agent-plus/blob/main/docs/maintenance/operations.md) |
| Generic tmux | Tmux Observer **0.6.0a9** + Tmux Plus **0.12.0a8** bundle; reader/bridge Mesh **0.1.0a24** | [Observer supply record](https://github.com/byebyebryan/tmux-observer/blob/13f6c9d76bb0202a131a0ee48aab0853f42709a0/docs/evidence/2026-10-23-public-delivery/README.md) and [Plus bundle record](https://github.com/byebyebryan/rofi-tmux-plus/blob/c75cc92e2d1cd67839a09818af18104ebd720df8/docs/evidence/2026-10-23-public-delivery/README.md) |
| RLCD hardware consumer | Its independent Observer **0.7.0a8** + Mesh **0.1.0a24** bundle | [Hardware operations](https://github.com/byebyebryan/esp32-rlcd/blob/main/projects/agent-dashboard/docs/operations.md) and [dated ticker trial](https://github.com/byebyebryan/esp32-rlcd/blob/edfb2fdfde9805d12b63384ee9145639890ba960/projects/agent-dashboard/docs/evidence/2026-10-21-age-ticker/REPORT.md) |
| Full diagnostic publishers / SSH authority | Independently selected by their deployment owner | [Historical role record](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#independent-installed-roles-at-the-2026-10-23-checkpoint) and current owner manifests |

The terminal reader requires already hosted working-set publishers/bridges and
explicit private source configuration. The dashboard requires its optional Textual
dependencies; finite CLI and diagnostic core/local-service users do not.
The terminal JSON interface is version 1. API 4, snapshot/watch 6, Service 4 and
working-set version-1 interfaces retain their separate contracts.

Agent Plus a17 fixes Claude default-home configuration selection. Its installed
package and host checks do not replace desktop appearance/input acceptance.
Tmux Plus a8 is bundle-only: use its exact Tmux Observer payload and module/hash
guard. A matching version string or historical inner-wheel digest does not
establish a published standalone wheel.

## What this checkpoint establishes

The a14 reader adds literal dashboard search across current cached repository
metadata, retaining the earlier session CLI and dashboard behavior. Its release
provenance binds qualified artifacts and checks. The owner's
[qualification boundary](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/dashboard.md#qualification-boundary)
retains the native and resource measurement limits. This presentation uses the
released application with fictional cached inputs; it adds no independent
native-classification, sustained capacity, resource or physical-device proof.

The a11 producer uses bounded clock uncertainty to recover quiet and first-seen
sessions across observed clock changes within one collector incarnation. The
[a11 provenance](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a11/provenance.json)
and [clock-recovery policy](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/working-set.md#clock-changes-and-recovery)
record the fix and its limits. Same-incarnation recovery was proved by an
installed-package regression; separate scoped deployment evidence records
recovery after normal restarts. No live clock adjustment, new independent native
classification or physical acceptance is claimed.

Operator-owned manifests retain effective host/home selections and rollback
inputs. This page changes no managed role. A ready service or successful cached
read cannot by itself prove native accuracy, complete fleet membership or
device acceptance. Directional host access stays directional; experimental
transport routes remain explicitly selected and independently qualified.

## Historical checkpoints

The earlier records remain fixed in Git, with their original observations and
limits:

- [2026-10-26 clock-recovery and scoped deployment](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#current-checkpoint--2026-10-26).
- [2026-10-25 coverage checkpoint](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#coverage-checkpoint--2026-10-25-historical).
- [2026-10-23 public release checkpoint](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#public-release-checkpoint--2026-10-23-historical),
  [independent installed roles](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#independent-installed-roles-at-the-2026-10-23-checkpoint)
  and [known bounds](https://github.com/byebyebryan/fleet-plus/blob/07e815ea198bfff1fb9b08a3e0270d7a905ebde6/docs/compatibility.md#known-bounds-at-the-2026-10-23-checkpoint).
- [Cross-project public-delivery closeout](https://github.com/byebyebryan/mesh-plus/blob/b306d44c329c6289781cc4db14f939ed2a4d20c2/docs/evidence/2026-10-23-public-delivery/README.md).

Those dated partial-membership and clock observations describe their checkpoints.
Keep their evidence intact while using the current owner guides for setup.
Observer writes, Claude monitoring and standalone active-only hosting remain
retired; working-set active membership and full diagnostics remain supported.

Sidebar/native composition, stress optimization and the extended soak remain
deferred. The [validation workflow](https://github.com/byebyebryan/agent-observer/blob/main/docs/maintenance/validation.md)
describes the independent evidence required to extend observation claims.
