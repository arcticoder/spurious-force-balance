# EasyEDA MCP bridge and the Spark competition (2026-10-29)

## easyeda-mcp-pro
- Package `easyeda-mcp-pro` 1.6.0 (PolyForm Noncommercial) needs Node 24.x (pinned 24.22.1) and checks at startup. `bunx` runs it with whatever `node` is first on PATH (shebang), so bun is fine but PATH decides: the failure was nvm's default Node 22.15.0.
- Fix applied: `nvm install 24.22.1`; the VS Code Insiders `mcp.json` entry sets `env.PATH` with `~/.nvm/versions/node/v24.22.1/bin` first and keeps `TOOL_PROFILE=pro`. `extension --open` then prints the `.eext` path (inside the bun/npm cache; also `extension --copy <dir>`).
- The user reported the bridge connected (2026-10-29); this session still had no easyeda tools (the server loads at session start). Originally unverified: the bridge connection. It needs the user to import the `.eext` in EasyEDA Pro, fully restart it, and click MCP Bridge > Connect; EasyEDA Pro (`easyeda-pro` in /usr/local/bin, a Windows install under WSL) must reach the server's WebSocket across the WSL boundary. The MCP tools only appear in a session started after VS Code reloads the server.
- Cheaper fallback if the bridge fights back: EasyEDA Pro imports KiCad files itself (File > Import).

## Spark 2026 (source: FabFlow blog, a third party with a referral link; the official OSHWLab pages are JS-rendered and returned only navigation text)
- Registration 2026-01-01 to 2026-11-30; judging December; $85,000 pool; categories include Best Documentation and Community Choice.
- Needs: design in EasyEDA (Pro), public on OSHWLab with schematics, layout, BOM, firmware, build instructions.
- Material sponsorship about 80% of manufacturing and shipping (PCB, PCBA, 3DP, CNC), duties and taxes the participant's; acceptance criteria not stated. $100 JLCPCB coupon per registrant; $50 each for referrer and referee when the referee submits.
- Every figure above is unconfirmed until read on the official page while logged in.

## Pictures
- Repo pictures are lossless JPEG XL (`.jxl`) since 2026-10-29; generators write a temporary PNG and call `tools/to_jxl.py` (needs `pillow-jxl-plugin` in `~/.venvs/lab-hw`). `cjxl` is not installed. GitHub does not render `.jxl` inline, so a README that must show a picture needs a PNG/WebP copy. `lab` has no committed PNGs (its `schematic.png` files are generated and gitignored).

## LFS
- `*.jxl` is LFS-tracked in both repos (`.gitattributes`); `lab` also keeps `*.jpg`. Neither repo tracked PNG. Existing .jxl were re-added with `git add --renormalize`.

## MCP client wiring
- The VS Code `mcp.json` configures VS Code's MCP client, not Claude Code. Claude Code reads `~/.claude.json` `mcpServers` (the `claude` CLI is not on PATH in the WSL shell, so the entry was written directly; backup in the scratchpad). A stdio `initialize` against `bunx easyeda-mcp-pro` under Node 24 answers correctly (v1.6.0). EasyEDA Pro itself runs natively in WSL (`/opt/apps/easyeda-pro`), so the bridge is localhost. Two clients running the server at once may fight over the bridge port.
- Spark rule from the user (2026-10-29): the design must be made in EasyEDA, not imported from KiCad/SKiDL; apply only after the redesign exists.

## Bridge state (2026-10-29, later)
- Connected through the VS Code `mcp.json` (key `servers`, not `mcpServers`); in a Claude Code session the tools appear as `mcp__easyeda-mcp-pro__*` after the server is up. `easyeda_health_check` reports bridge_connected with EasyEDA Pro 1.6.0 extension.
- With nothing open, `schematic_components` fails and `canvas_capture` returns no image; every tool wants a `projectId` and there is no tool to create or list projects (only API inventory names `dmt_Project`), so the user must open a project first.
- Tool limits that shape the redesign: schematic writes (place_component, connect_pin_to_net, batch_write, net flags) exist; the PCB side is read-only plus DRC and autoroute; footprints reach the PCB only through `schematic_sync_to_pcb`, whose confirmation dialog the user must click. Custom board outlines, the 208 mm arm shape, placement and copper for the mechanical boards probably need EasyEDA's own UI or the extension API; check `api_inventory` filtered on PCB_ before promising it.

## Project file and profiles
- `hardware/easyeda/spurious-force-balance.eprj2` is a SQLite database (tables: boards, components, ...; 389 KB empty), rewritten on every save, so diffs are opaque: tracked through Git LFS (`*.eprj2` in `.gitattributes`), committed at milestones only, not every save. The OSHWLab copy is uploaded from EasyEDA itself, not from git.
- `canvas_capture` works with the project open (empty PCB, mil grid). The PCB API (`api_inventory` filter `PCB_`) has create/modify for components, pads, lines, polylines, pours, vias, regions; the `pro` profile exposes none of them. `full` adds "controlled documented API method calls" and CircuitIR floorplanning, so the profile was switched to `full` in the VS Code mcp.json (needs a restart). `dev` adds probes; avoid unless debugging.
