# Compatibility and evidence

This guide preserves the reviewed **2026-10-23** checkpoint and adds a current
**2026-10-26** update. Public release records bind artifact and qualification
inputs; installed selections remain in operator-owned manifests. Source revision,
public release, installed selection, native evidence, consumer behavior and
physical acceptance are separate checkpoints.

## Current checkpoint — 2026-10-26

Agent Observer **0.7.0a11** adds bounded recovery across observed clock changes.
Quiet and first-seen sessions no longer require new activity solely because
the collector detected a clock discontinuity. The producer preserves uncertain
proof boundaries, nonrenewing expiry, exact native/support joins and the existing
API 4, snapshot 6, Service 4 and working-set 1 schemas. Mesh remains **0.1.0a25**.
See the [a11 release](https://github.com/byebyebryan/agent-observer/releases/tag/v0.7.0a11),
[artifact manifest](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a11/observer-0.7.0a11.json)
and [provenance](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a11/provenance.json).

The operator-owned selection at dotfiles commit `f5c4782` advances collectors,
the public reader and working-set bridges to a11. Snap Default/Work and Starship
have verified installed bytes, clean scoped managed status and complete cached
coverage after deployment. Snap also passed rollback/reselection. Carbon is
offline and its rollout remains pending. Full publishers retain Observer a5 /
Mesh a20; the dashboard retains Observer a8 / Mesh a24. No reverse host route
or experimental transport was enabled.

The source/package regression proves recovery across a simulated clock step
within one collector incarnation; a normal deployment restart is separate
evidence. The offset range covers accepted mappings in that incarnation, not
unobserved historical clock excursions. Live clock changes, new independent
native classification and physical-device acceptance are not claimed. The
[clock-recovery guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/working-set.md#clock-changes-and-recovery)
defines the policy and limits.

## Coverage checkpoint — 2026-10-25 (historical)

Agent Observer **0.7.0a10** publishes working-set coverage reasons with the API 4,
snapshot 6, Service 4 and working-set 1 contracts unchanged. Its paired Mesh
remains **0.1.0a25**. See the [a10 release](https://github.com/byebyebryan/agent-observer/releases/tag/v0.7.0a10),
[immutable Observer wheel](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a10/agent_observer-0.7.0a10-py3-none-any.whl),
[artifact manifest](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a10/observer-0.7.0a10.json)
and [release provenance](https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a10/provenance.json)
for exact inputs and qualification evidence. The current [working-set guide](https://github.com/byebyebryan/agent-observer/blob/main/docs/guides/working-set.md)
explains membership, coverage and bounded reads.

The operator-owned private selection at dotfiles commit `d4d780b` enables the
a10 / Mesh a25 working-set reader on Snap, Starship and Carbon. Independent
selections remain: full publishers use Observer a5 / Mesh a20; the dashboard
uses Observer a8 / Mesh a24.

Oct 25 cached producer/Mesh reads show complete working-set coverage for Starship
and Snap Default/Work; Carbon is partial with reason `clock_discontinuity`.
Carbon's cached inventory reported complete source coverage and included parked
threads. The exact historical clock event was not retained and remains
unattributed. Later stable clocks do not clear guards for unchanged native
activity. These scoped cached reads establish neither permanent fleet
completeness nor new independent native or physical qualification.

## Public release checkpoint — 2026-10-23 (historical)

| Role | Reviewed public input | Owner evidence |
| --- | --- | --- |
| Agent collector and working-set publication | Agent Observer 0.7.0a9 + Mesh 0.1.0a25 | Public delivery closeout below |
| Native agent entry | Agent Plus 0.15.0a15 | Its release and removed-host correction |
| Generic tmux | Tmux Observer 0.6.0a9 + Tmux Plus 0.12.0a8 bundle; Tmux Mesh reader/bridge 0.1.0a24 | Tmux supply/acceptance records below |

The [2026-10-23 public delivery closeout](https://github.com/byebyebryan/mesh-plus/blob/b306d44c329c6289781cc4db14f939ed2a4d20c2/docs/evidence/2026-10-23-public-delivery/README.md)
records exact release assets, fresh public downloads, CI and scoped managed
convergence. Existing qualified bytes were published without rebuilding or
replacing historical releases. Observer writes and standalone active-only hosting
are fully retired; working-set active membership and full diagnostics remain.

- [Agent Observer a9](https://github.com/byebyebryan/agent-observer/releases/tag/v0.7.0a9)
  and [Mesh a25](https://github.com/byebyebryan/mesh-plus/releases/tag/v0.1.0a25).
- [Agent Plus a15](https://github.com/byebyebryan/rofi-agent-plus/releases/tag/v0.15.0a15)
  and [removed-host correction](https://github.com/byebyebryan/rofi-agent-plus/blob/35eeadaff286f20ee631c2240587536647c8248d/docs/removed-host-rows.md).
- [Tmux Observer a9 supply inputs](https://github.com/byebyebryan/tmux-observer/blob/13f6c9d76bb0202a131a0ee48aab0853f42709a0/docs/evidence/2026-10-23-public-delivery/README.md)
  and [Tmux Plus a8 bundle inputs](https://github.com/byebyebryan/rofi-tmux-plus/blob/c75cc92e2d1cd67839a09818af18104ebd720df8/docs/evidence/2026-10-23-public-delivery/README.md).

Tmux Plus a8 is bundle-only. Its historical inner-wheel digest does not imply
that a matching standalone wheel was published. Install/verify the exact owning
bundle and Observer pin rather than substituting a source build with the same version.

## Independent installed roles at the 2026-10-23 checkpoint

At that checkpoint, the full Agent publisher retained Observer a5 / Mesh a20,
the dashboard retained its reviewed Observer a8 / Mesh a24 bundle, and SSH
authority retained its independent Mesh a6 selection. These are intentionally
different roles, not a request to upgrade them all to the newest package.

Private operator-owned deployment manifests record effective host/home selections
and rollback inputs. A current service status alone establishes neither complete
source coverage nor device acceptance.

## Known bounds at the 2026-10-23 checkpoint

The closeout reported **partial / membership_incomplete** for Carbon working-set
membership, with a ready full cached service. Its root cause remained unresolved.
That is neither a complete-empty roster nor proof of a deployment regression.
The checkpoint's other accepted reads retain their own endpoint and time scope.

Native collection, installed bytes, consumer behavior, graphical acceptance and
physical panel/reboot checks are separate. This website adds no new runtime or
physical qualification. The [validation workflow](https://github.com/byebyebryan/agent-observer/blob/main/docs/maintenance/validation.md)
explains the independent evidence required for new observation claims.
