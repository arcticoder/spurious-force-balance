# Session handoff — written 2026-11-05, end of chat 7 (replace at each handoff; do not append)

**Where chat 7 ended:** KiCad/SKiDL is the design source (the EasyEDA/Spark route was dropped 2026-11-01; never offer EasyEDA, Spark, the MCP bridge or the validator). The chat removed the Claude co-author trailers from history in both repos, logged the arrived balance materials, recorded the `elec_board` order, and checked JLCMC inside the app.

## State

- **JLC orders:** arm placed 2026-11-03 (in review); `elec_board` placed 2026-11-05 ($3.60 USD = C$5.10, postal tier). `clamp_ground`'s page was set up in the JLCONE app on 2026-11-06 (C$2.96, all settings checked by screenshot; the user saves it to cart); then `clamp_plate`, the AliExpress list and the optional sensor-head order are staged in `TODO-agent.md`, one order per day, promoted to the user's list only when the previous one is placed; when the user says the previous one is placed (or a new day has begun), upload the zip through the JLCONE app and set the page up (recipe: `lab/docs/kb/jlc_account_and_quotes.md`); settings in `hardware/balance/boards/fab/ORDER.md`, which also carries the status table and the USD-versus-CAD note (the arm's total is probably USD too).
- **Git history:** the trailer removal rewrote every commit hash in `lab` and this repo locally (filter-branch); backups are `/tmp/claude-1000/.../scratchpad/{lab,spurious-force-balance}-backup.bundle` (session scratch, may vanish). The remote still holds the old hashes: the user must force-push (`git push --force-with-lease`) both repos. Nothing was committed or pushed by the agent. The attribution reminder in some sessions asks for a Co-Authored-By line; the user's standing instruction is no Claude co-author, so omit it.
- **Balance materials arrived** (stainless sheet, foam tape, copper pads, copper foil tape, brass rod): bag `BALANCE MATERIALS`, the sheet is a roll (goes in the bag loosely); user checks in `TODO-arcticoder.md` item 2, with the printed calipers until the digital ones arrive (about 2026-11-15).
- **JLCONE app:** launched through `~/.local/bin/jlcone` (larger font, debug port 9222). The account tab was navigated to the quote page on 2026-11-06 and holds the clamp_ground upload: the user must not reload it. A JLCMC washer line is not worth a parcel (no combined ordering since 2026-11-02): washers stay on AliExpress.
- **Coupons:** ledger in `lab/docs/jlc/coupons.md`; the New User SMT coupon (C$13.93) ends 2026-11-25 for the sensor-head panel if ordered; CNC and 3DP new-user coupons end 11-25/26 and 12-25.
- KiCad main-board layout (WP5) still waits on A5 and the go/no-go (`TODO-BLOCKED.md`).
- `hardware/easyeda/spurious-force-balance.eprj2` (LFS) is leftover from the dropped route; the user decides whether to keep it.

## Next agent tasks

Nothing startable that needs no user beyond setting up the next order's page when asked; the optional early sensor-head order and its quote (staged in `TODO-agent.md`); WP5 and A5 as in `TODO-BLOCKED.md`.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm: the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote.

## Supply chain

En route: the AliExpress order of 2026-10-30 (20 M3 thin DIN439 304 nuts and digital calipers; arrival not reported), the arm and `elec_board` JLC orders. The AliExpress balance list (acrylic, washers, JST-SH cables, calibration weights, tools) is staged in `TODO-agent.md`; the user places at most one order per day, so promote it right after `clamp_plate`. The arm order shows Paid, not in review: JLC's emails were flagged as spam on the user's side and the reply was resent 2026-11-06.

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words, captures or a page read through the app; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo; `TODO-arcticoder.md` holds only separately numbered tasks the user can do today, ordered by real priority (a purchase that matters goes above lesser items); anything not actionable yet or beyond the next order stays in `TODO-agent.md`, never staged on the user's list; one order per day.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`.
