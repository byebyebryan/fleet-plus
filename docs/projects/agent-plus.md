# Agent Plus

Find your Codex and Claude environments, then open or focus their native TUIs.
One searchable Rofi picker covers local environments and configured SSH hosts.

<!-- fleet-plus:agent-picker -->
![Agent Plus Rofi picker showing example local and remote environments and native TUI windows.](../../assets/agent-plus.png)

*Actual Rofi rendering with sample data and a preview theme. No live sessions are
shown; your Rofi theme controls its appearance.*
<!-- /fleet-plus:agent-picker -->

## Native managers remain the daily interface

Agent Plus discovers environments and tracks its own dedicated windows. Open
focuses the exact selected registered window or enters its environment; New window
creates an independent native TUI client. Native Codex/Claude managers own the
conversations, work, settings and authentication inside those windows.

Inventory is about environments and window ownership. It is different from
Agent Observer's read-only conversation/runtime observations. Agent Plus needs
neither Agent Observer nor Tmux.

## Local and remote entry

SSH Plus supplies logical hosts and routes. A fixed Agent Plus host helper runs
on each remote provider host, so each TUI opens alongside its owning native runtime.
Removed peers are excluded from cached environment discovery and warnings;
an existing registered window does not grant access to a removed host.

## Start using it

The supported desktop is Linux with Niri and dedicated Kitty windows. Requires
Python 3.11+, Rofi 2.0+ and a provider CLI supporting `codex agents` or
`claude agents`. Remote use also needs OpenSSH, SSH Plus and the host helper on
the remote noninteractive PATH.

Follow the [repository setup](https://github.com/byebyebryan/rofi-agent-plus#install),
[configuration example](https://github.com/byebyebryan/rofi-agent-plus/blob/main/examples/direct.toml)
and [current architecture](https://github.com/byebyebryan/rofi-agent-plus/blob/main/docs/architecture.md).
The Python package has no runtime Python dependencies.

## Supported scope

Agent Plus recognizes windows it launched. Arbitrary manually launched TUIs,
other terminal backends, Mosh and picker-driven Close remain outside the current
supported path. Claude native entry is supported independently of Observer's
retired Claude monitoring.

The a15 release and removed-host correction have independent source, installed
and managed evidence; see the [compatibility guide](../compatibility.md).
