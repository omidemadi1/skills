# Project learnings — Shadow Box (2026-10)

> **Project-specific.** These notes are not general rules for other projects. The reusable
> engineering facts from this build were promoted to `references/learnings.md`; this file keeps
> the post-mortem, the cost anomaly and the hand-off items.
>
> Project folder: `Business/Shadow Box/` · BOM: `one-piece-gear5-shadow-box - V6.md` · Log: `Journal.md`

## What the project was

An A4 LED shadow box: a printed poster with the white areas cut out, backlit by a 12V 5050 strip,
USB-C powered, touch on/off, in a shallow frame.

## Process failures → rules

| What happened | Root cause | Rule now in the skill |
|---|---|---|
| Bought a 220V strip + expensive connector, then switched to 12V | Power path chosen before comparing it | Design the power path first (Gate 2) |
| MT3608 ran at its limit, dim/hot | No V/A/W budget, no derating | Budget + ≤60% derating (Gate 2) |
| TTP223 could not switch the LEDs | Logic output vs load ignored | Interface check (Gate 5) |
| 80W unregulated iron melted strip pads | Tool capability mismatch | Tool-task fit rule |
| Glue stick failed under heat, then hot glue | Adhesive service temperature ignored | Adhesive matrix |
| Milky acrylic "made the light yellow" | Confused diffusion with CCT | Specify CCT/CRI separately |
| Pin headers failed twice | Wrong joining method | Connector → solder → never headers |
| Enclosure designed after wiring | Sequence error | Enclosure-first + mock-up |
| A3 paper board used as structure | Material grade ignored | 6mm MDF/plywood for permanent |
| Cost table mixed Rial/Toman, mixed date formats | No ledger discipline | Cost ledger rules |
| Print, plexi, diffuser, bazaar items missing from costs | Scope not captured | Missing rows are findings |
| No voltage/current measurements | No instrumentation | Multimeter in Wave 0 |
| No labor hours recorded | Not tracked | Labor log |
| Repeated rework and re-buys | Full BOM before spike | Wave 0 spike |

## Cost-table anomaly

Six rows dated 1405/04–05 look 10× too high (Rial entered as Toman). The recorded total was
**25,280,854**; the plausible total is **5,311,596**; first-unit **5,311,596**; batch estimate
**~1,128,554** before print, plexi, diffuser, MOSFET, enclosure and packaging. Always verify the
scale against the invoice before adding a row to a total.

## Open items at hand-off

- USB-C **PD trigger 12V** or a 12V adapter (replace the MT3608 for the strip load)
- Logic-level MOSFET (AO3400 + gate resistor/pulldown) **or** a ready 12V touch dimmer
- Solderless 8/10mm strip connectors
- Fuse/polyfuse and the right heat-shrink diameter
- Enclosure (6mm MDF/plywood), diffuser, packaging
