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
