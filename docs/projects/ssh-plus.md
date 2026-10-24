# SSH Plus

A Rofi picker for SSH destinations, plus the public Host Mesh interface used by
the related tools. Keep SSH access and configured route authority in one place.

## A useful host list

The picker remembers destinations that have actually answered an SSH reachability
check. It does not enumerate every entry in SSH configuration or known_hosts.
SSH Plus owns successful-connection history, navigation and connection UX.

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
Follow the [repository installation and configuration](https://github.com/byebyebryan/rofi-ssh-plus#install-and-invoke)
and [Host Mesh guide](https://github.com/byebyebryan/rofi-ssh-plus/blob/main/docs/reference/host-mesh-v1.md).

The public process contract, authority selection and picker history have separate
owners. Updating an unrelated Observer or dashboard does not replace the SSH
authority's independently selected package.
