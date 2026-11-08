# SSH Plus

A Rofi picker for SSH destinations, plus the public Host Mesh interface used by
the related tools. Keep SSH access and configured route authority in one place.

## A useful host list

The picker remembers destinations that have actually answered an explicit SSH
reachability check. It does not enumerate every entry in SSH configuration or
known_hosts. SSH Plus owns usage history, navigation and connection UX.

## Seven-day Connect ordering

Each desktop keeps its own SSH Plus history. A Connect counts once only when its
bounded probe reaches an SSH server; multiple configured route attempts still
represent one Connect. Background route-health reports and Agent Plus transports
do not count.

If any listed host has a successful Connect in the rolling 168-hour window,
weekly counts sort descending. Ties retain the existing managed declaration
order and ad-hoc name order; last-used time never breaks a weekly-count tie. If
all listed hosts have zero weekly Connects, retained last-used times sort them,
with never-used hosts last. The most recently used listed host is highlighted
independently of weekly rank, with the first ranked row as fallback. The native
launcher freezes row ordering during the dialog; a new dialog captures current
usage.

The new history schema starts fresh and leaves the former generic and DMS files
untouched for rollback. It does not import their old records or lifetime counts.
Close and reopen a picker that was already open during the schema upgrade; its
old action state is safely rejected until refreshed. Existing SSH terminals and
native provider sessions continue independently.
The owner [usage guide](https://github.com/byebyebryan/rofi-ssh-plus/blob/main/docs/guides/usage.md)
describes counting, Forget history and launcher behavior.

Mesh implements the shared host/route authority behind the canonical Host Mesh v1
process facade. Consumers call `rofi-ssh-plus mesh ... --json`; they do not import
picker internals or maintain a second registry.

## Related workflows

- Open a configured SSH destination in your terminal.
- Supply routes for native Agent Plus entry.
- Supply logical host membership for Mesh and generic Tmux clients.

Each endpoint's roster is directional. Reaching a machine does not grant it a
route back to you. See the [directional example](../architecture.md#directional-host-access).

## Start using it

Requires Python 3.11+, Rofi 2.0+, OpenSSH and a terminal accepting `-e`.
The default authority backend requires a compatible Mesh installation.
Follow the [current getting-started guide](https://github.com/byebyebryan/rofi-ssh-plus/blob/main/docs/getting-started.md)
and [Host Mesh guide](https://github.com/byebyebryan/rofi-ssh-plus/blob/main/docs/reference/host-mesh-v1.md).

The public process contract, authority selection and picker history have separate
owners. Updating an unrelated Observer or dashboard does not replace the SSH
authority's independently selected package.
