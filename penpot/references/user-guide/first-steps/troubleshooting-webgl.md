# Troubleshooting WebGL

### WebGL rendering (Beta)

Since **Penpot 2.16**, optional **WebGL rendering (Beta)** is available on `design.penpot.app` and self-hosted instances. It is **off by default**.

Turn it on from **Your account → Settings** or **Workspace → Main menu → Preferences** when you want a faster canvas for complex files.

In this beta, WebGL applies to the **design workspace canvas** only. View mode and exports still use the legacy renderer, so some visual differences are expected. If the beta gets in your way, you can switch back to the legacy renderer at any time.

For what is in scope today, what we are prioritizing next, and known visual differences, read [What's next for the Penpot WebGL renderer](https://community.penpot.app/t/whats-next-for-the-penpot-webgl-renderer/10627) on the Penpot Community.

When WebGL rendering (Beta) is enabled, Penpot uses WebGL to render the design workspace canvas. If WebGL is unavailable in your browser, Penpot cannot use that renderer and the workspace canvas may not open correctly.

Sometimes WebGL appears enabled in your browser, but Penpot still cannot create a graphics context. This is usually related to browser settings, GPU acceleration, drivers, or temporary GPU overload.

## Before changing anything

1. Open [https://get.webgl.org](https://get.webgl.org/).
2. Check the result:
   - If you see a spinning cube, WebGL works at browser level.
   - If it fails (blank page, error message, or no animation), continue with browser and system checks below.

## Quick checks (2 minutes)

1. Close graphics-heavy tabs/apps (video editors, 3D apps, many design tabs).
2. Reload Penpot.
3. Fully restart the browser.
4. If needed, restart your computer.

Why this helps: GPU memory or context slots can be temporarily exhausted, even when your configuration is correct.

## Chrome

1. Open `chrome://settings/system`.
2. Turn on **Use graphics acceleration when available**.
3. Restart Chrome.
4. Open `chrome://gpu` and review WebGL-related warnings.

Why this helps: WebGL depends on hardware acceleration and a healthy GPU process.

## Mozilla Firefox

1. Open Firefox and check that zoom is set to **100%** from the top-right menu.
2. From that same menu, open Settings/Preferences.
3. In General settings, confirm Firefox is up to date and run **Check for updates** if needed.
4. Enable hardware acceleration in Firefox settings.
5. Restart Firefox.
6. Open `about:support` and review the Graphics/WebGL section.

Why this helps: outdated browser builds, disabled acceleration, or blocked GPU features can prevent context creation.

## Safari

1. Update Safari/macOS to the latest available version.
2. Restart Safari.
3. Re-test in [https://get.webgl.org](https://get.webgl.org/).

Why this helps: Safari WebGL behavior is strongly tied to OS/browser version and graphics stack updates.

## Settings

Some advanced browser configurations or experimental settings can interfere with WebGL. If you have modified these in the past, consider restoring default browser settings or testing in a fresh profile.

## About zoom and trackpad settings

In some cases, changing browser zoom or trackpad settings is suggested as a workaround.

In Penpot, these are **not baseline requirements** for WebGL. Treat them only as temporary diagnostics if support explicitly asks for them.

If you temporarily changed one of these settings and Penpot starts working, you can usually revert it and test again.

## GPU drivers and OS checks

1. Install any pending OS updates.
2. Update GPU drivers (especially on Windows/Linux).
3. Disable graphics overlays/tools (recording overlays, GPU tuning utilities) and test again.

Why this helps: outdated or conflicting graphics layers can break WebGL context creation.

## Known edge case: Linux + Nvidia

Some Linux + Nvidia combinations can report WebGL as available but still fail at runtime in specific browser/driver combinations.

In some cases, switching between proprietary and open-source drivers or updating the NVIDIA driver resolves the issue.

If this is your setup, collect diagnostics and contact support.

## If the issue persists

If WebGL rendering (Beta) is blocking your work, turn it off in **Your account → Settings** or **Workspace → Preferences** and continue on the legacy renderer while you report the issue.

Please share:

- Whether WebGL rendering (Beta) is enabled or disabled.
- Browser and version.
- Operating system and version.
- Result from [https://get.webgl.org](https://get.webgl.org/).
- A screenshot of browser graphics diagnostics (`chrome://gpu` or `about:support`).

Then contact us at [support@penpot.app](mailto:support@penpot.app) or open a GitHub issue at <https://github.com/penpot/penpot/issues>.
