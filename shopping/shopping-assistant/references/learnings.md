# Shopping Assistant — Learnings (live)

> Proven, project-tested knowledge. **Read this before the first search of a new project.**
> Sections mirror `learnings-template.md`. Add a dated line whenever something new is proven on a
> real order — that is how this file earns its keep.
>
> Examples come from past builds; treat them as defaults to check, **not** as rules that must apply
> to the current product. Anything true for only one project belongs in `references/projects/`.

## Material Preferences

- **Pre-cut beats raw stock for a first unit.** A 30×40cm MDF 3-pack (219,000, Digikala) is better
  than a full 244×183 sheet while prototyping; buy the sheet once the box is final.
- **Wire:** single-conductor stranded copper, 0.5–0.75mm², ~2m, for a small LED build; colour does
  not matter to the user. (`سیم برق افشان 1×0.75` — 24,000 for the base length, the 2m variant bills
  at 48,000.)
- **Heat-shrink must match the strip width:** ~11mm sleeve for 10mm-wide 5050 strip, plus a mixed
  6-size kit for the small joints. Bulk 150–330-piece kits are waste — a 334,000 kit was rejected.
- **Packaging:** a **two-piece rigid hard-box (کف + درب)** in white covered cardboard — not a plain
  shipping carton — with black **PE** foam thick enough to rout cutouts (2–3cm).
- **Power for a USB-fed LED product:** for a **5V** load, the customer uses their own 5V ≥2A
  charger; ship no adapter. For a **12V** strip, do not boost from 5V — use a USB-C PD trigger
  (12V) for a product, or a 12V adapter + DC jack for a prototype.

## Common Mistakes

- **Never recommend a part from its title.** «ترمینال فشاری» (74,500) and «کانکتور پیچی SP1 بستهٔ ۲۵
  عددی» (67,000) are not the same class of part — see *Electrical parts* below.
- **Don't add "just in case" duplicates.** The user prunes them and the cart then looks careless (a
  second terminal, a 334,000 heat-shrink kit and wood glue were all removed by the user).
- **Don't promise cart deletions.** Icon-only remove controls are unreachable by the automation.
- **Don't compare a Digikala price read today with a Basalam price read last week.** Re-read the
  live cart page before quoting a total.
- **Don't trust one MCP search.** Digikala's ranker returns the same top-N for quite different
  queries; if two searches look identical the term is being ignored.

## Electrical parts — read the spec, not the title

Persian component titles are marketing; the deciding text is the spec line:

- `۲ خانه دو طرف فشاری` = 2 cells, push on both sides = **2 in / 2 out** ✅ — «ترمینال فشاری مدل T6»,
  dkp-4560351, 53,990–79,000, 143 ratings.
- `کانکتور پیچی SP1` = a single 2-wire splice, **1 in / 1 out** ❌ — literally "خروجی نمیده" (no
  output to branch from). Good only for joining two wires in line.
- `ترمینال برق شاخهای / نواری چندخانه` = a barrier strip; every house has 2 screws (in + out) and
  the strip is cuttable — «ترمینال برق اورانوس ۶A», dkp-5146262, 158,810, 452 ratings; Basalam
  equivalent ~71,400.
- **Size guide:** a 6A strip is plenty for a 12V/~1A LED build; don't pay for 16A.
- **Star/bus to 3 strip pieces:** one 2-cell terminal per rail is not enough. Either bridge adjacent
  houses with short jumpers, or use a multi-port connector (PCT-215 = 5 ports on one node, ~20,000).
- Voltage-matching modules (MT3608 5V→12V boost) exist on both platforms; Basalam is usually
  15–40% cheaper for the identical module.

## Site Insights

| Category | Cheapest / best | Notes |
|---|---|---|
| Raw materials, adhesives, wiring, stationery, small components | **Basalam** | 2–10× cheaper than Digikala on the same item |
| Tools with warranty, mainstream electronics | **Digikala** | 7-day returns, real ratings, fast delivery |
| Expensive tools (multimeters, strippers) | **Torob** for price, Digikala for warranty | a Torob card shows the cheapest shop only |
| Black PE foam, routed | persianfoam.co · pasargadfoam.com · naxhome.com · needsanat.com | not on the marketplaces |
| Rigid hard-box (کف+درب) | banichap.com · afragraphic.com · tarhheram.com · kamelpack.com | Basalam only has small gift boxes |
| Diffuser sheet | mrplexi.ir (ask for برش تکی) | tracing paper (کاغذ کالک) is the cheap alternative |
| Glossy A4 print | haftmehr.ir · axprint.com | order 3 backups |

Price gaps measured on one project (same item, both platforms): tracing paper 250,000 → **18,000**;
hot-glue sticks 93,000 → 21,000; wire cutter 495,000+ → 286,000; USB-C panel socket 140,000 →
55,000; 2-pin terminal 74,500 → 8,000; boost module 109,000 → 92,000; matte black spray 250,000 →
176,400; metal ruler 130,000 → 50,000; wood glue 110,500 → 69,900.

## Platform Notes — carts, minimums, payments

- **Digikala:** cart is flat (one row per item) with the totals in the footer. An unpaid cart is
  dropped item-by-item as stock runs out → tell the user to pay promptly. The per-row remove is an
  **icon-only control**, unreachable by automation — the user must click it.
- **Basalam:** the cart is grouped **per storefront (غرفه)** and **each storefront has its own
  حداقل خرید**. A 3-غرفه cart can be blocked because one is 29,000 short; the `بررسی حداقل خرید`
  button lists exactly which. No ratings on Basalam → use `sales_count`.
- **Payments are always the user's.** The assistant builds and verifies carts; the user logs in and
  pays. Never click checkout, never touch address forms.
- **Never remove items the user didn't ask to remove**, and never empty a cart to "tidy up".

## Tool Inventory

> Fill from the user's answers; never re-list owned tools. Capability matters more than the name.

- Soldering iron: 80W Takachihu, **unregulated** — not suitable for LED pads; a temperature-
  controlled station is the upgrade.
- Hot-glue gun: ABC-E20W + sticks.
- 4.5" mini wire cutter (Kron).
- Breadboard + 65-piece jumper kit.
- TTP223 touch modules (10-pack).
- Pencil-style knife (Shineway) + blades.
- Digital multimeter: **not owned yet** — required for any electrical build.

## Pricing Benchmarks (2026-10, Toman)

| Item | Price | Source |
|---|---|---|
| MDF 3mm, 30×40cm, 3-pack | 219,000 | Digikala |
| LED strip 12V 5050, 1m | 216,600 | Digikala |
| LED strip 12V, 5m | ~695,000 | Digikala |
| MT3608 boost module | 92,000 / 109,000 | Basalam / Digikala |
| Fixed 5V→12V boost module | 144,400 | ageniz.com |
| USB-C panel socket | 55,000 / 140,000 / 52,000 | Basalam / Digikala / Torob |
| Terminal strip «اورانوس ۶A» (12 houses) | 158,810 / 71,400 | Digikala / Basalam |
| Two-piece rigid hard-box ~36×27×6cm | استعلام | specialist |
| Black PE foam, routed | استعلام | specialist |
| TTP223, 10-pack | 230,000 | Digikala |
| Heat-shrink, 3m | 281,000 | — |
| Wire 2×0.5, 2m | 135,000 | — |
| Solder 50g (Asahi CF-10) | ~404,936 | recorded 4,049,364 = likely 10× |
| Soldering iron 80W | ~638,780 | recorded 6,387,800 = likely 10× |

> ⚠️ Six rows in the Shadow Box ledger dated 1405/04–05 look 10× too high (Rial entered as Toman).
> Verify the scale against the invoice before adding a row to a total.

## Supplier Notes

- All prices in **Toman**; all marketplace queries in **Persian**.
- This user's projects live in an Obsidian vault, one folder per product, versioned per revision
  (`<project> - V<n>.md`). Read the newest, write the next, keep section numbers stable.
- Persian text through a PowerShell console gets mangled: build Persian strings from `[char]0x…`
  codepoints and read saved UTF-8 files with a file reader, never `Get-Content`.

---

# Proven engineering facts (reusable)

> Measured on a real build, but stated as general rules. They apply to any project that uses the
> same component class. The project-specific post-mortem is in `references/projects/`.

## Power path — proven ladder

| Load | Best path | Avoid | Note |
|---|---|---|---|
| 5V, ≤0.5A | USB-C direct | — | A dumb USB-C device gets only 0.5A without 5.1kΩ CC pulldowns |
| 5V, >0.5A | 5V ≥2A charger, or PD trigger 5V | boost | Watch voltage drop on long cables |
| 12V, ≤0.5A | USB-C **PD trigger 12V**, or 12V adapter | MT3608 if possible | Measure the module temperature |
| 12V, >0.5A | 12V adapter 1–2A, or PD trigger 12V | MT3608 | Derate to ≤50–60% |
| 220V | Certified driver only | Any handmade mains wiring | Shock/fire risk; not worth it |

- **MT3608 is a 2A-switch module, not a 2A output.** At 5V→12V the practical output is roughly
  0.5–0.7A, and it runs hot near that. A 53cm 5050 strip (~0.6A) sits right at the edge — that is
  why it dims/flickers/heats. Use a PD trigger or a 12V adapter instead.
- **USB-C without 5.1kΩ from CC1 and CC2 to GND** may refuse to supply more than 0.5A. Many panel
  sockets omit them. Check the socket or add the resistors.
- **Fuse** at 1.5–2× the load; **strain-relieve** every cable that leaves the box.
- **Voltage drop** target: <5% at the last branch (0.6V at 12V, 0.25V at 5V).

## LED and optics — proven

- **5050 12V, 60 LED/m: ~14.4W/m ≈ 1.2A/m.** 53cm ≈ 0.6A. 2835 is ~7–10W/m; COB gives an even
  line with no dots and is the better choice when the diffuser must sit close.
- **Diffusion is not colour.** A milky/opal diffuser does not make white light yellow. Yellow
  output means a warm-white strip (~3000K), an aged sheet, or a tinted backing. Specify **CCT**
  (6000–6500K for neutral white) and **CRI** separately.
- **Standoff 15–25mm** between strip and diffuser; white reflective cavity behind the strip.
- **Each diffuser layer costs ~10–15% of the light.** Two layers (milky acrylic + diffuser) lose
  15–25% and still do not fix colour. Use one good diffuser.
- **Cut only on the marked lines**; the copper pads are not continuous.

## Soldering and joining — proven

- **350°C max, 2–3 seconds per joint, pre-tin pad and wire, flux, 0.5–0.8mm solder.** An
  unregulated 80W iron exceeds 400°C and delaminates the pad / melts the strip body.
- **Solderless connectors (8/10mm) beat soldering** for serviceability and for anyone without a
  temperature-controlled iron. Use solder only for middle cuts and permanent harnesses.
- **Pin headers do not work** for joining a wire to a strip pad: the pin does not grip the pad and
  the strands do not grip the pin. This was tried and failed twice.
- **Heat-shrink ~11mm** for 10mm-wide 5050 strip. Test every joint: ~1kg pull for 10s, <1Ω.
- **Strain-relieve** the cable so the solder joint carries no load.

## Switching — proven

- **A TTP223 output sources only a few mA** and cannot switch a strip. Use a **logic-level
  MOSFET** (e.g. AO3400) with a 100–220Ω gate resistor and a 10kΩ pulldown, plus 100nF at VCC and
  100–470µF near the strip. Or, simpler, use a **ready 12V touch dimmer module**.
- TTP223 has a **toggle/momentary solder jumper**; decide the behaviour before wiring.
- A random IRF MOSFET may not fully turn on at 3.3V — check the gate threshold.

## Adhesives — proven

| Adhesive | Service temp | Use for | Never for |
|---|---|---|---|
| Glue stick | ~50°C | Paper, temporary positioning | LED strip, anything warm |
| Hot glue | ~60–80°C | Cable tacking, prototypes | LED strip in a closed box |
| 3M double-sided tape | ~90°C+ | LED strip, panels | Dirty/porous surfaces |
| Neutral silicone | ~200°C | Permanent LED fixing, glass | Fast production (cure time) |
| Epoxy | ~120°C+ | Structural joints | Repairable assemblies |

The strip already has 3M backing; add silicone at the ends for a permanent fix. Hot glue softens
and yellows; a glue stick is for paper, not for a warm strip.

## Enclosure and mechanical — proven

- **Design the enclosure before the wiring.** Panel-mount connectors, cable exits and service
  access are set by the enclosure; wiring around a finished box causes rework.
- **Build a full-size cardboard mock-up first.** Thirty minutes prevents a re-cut.
- **3mm MDF/board is a prototype material** — it warps. Use 6mm MDF or plywood for a permanent
  frame. Paper-faced backing board is not structural.
- **Stack-up needs numbers:** back panel + wiring + LED + standoff + diffuser + print + front +
  frame, with 2–3mm clearance.
- **Serviceability:** the unit should open without desoldering; use a connector between the back
  panel and the strip harness.

## Cutting and printing — proven

- Glossy/photo-glossy prints: **fresh blade per print**, cut from the back, steel ruler and
  cutting mat. A dull utility blade tears fibres and leaves a white edge.
- A pencil-style knife gives better control on curves than a snap-off knife.
- More than two identical pieces → plotter/vinyl cutter with registration marks, or laser/CNC.
- Print **one** test copy before committing a batch; photo-glossy and glossy behave differently.

## Measurement benchmarks

- A **multimeter is mandatory** for any electrical build (DT9205A / UNI-T UT136B+ ≈ 300K–1M).
  Without it, every later decision is a guess.
- Targets: output within **±5%**; driver case **<60°C after 10 min**; no flicker for **30 min**;
  joint **<1Ω** and **~1kg pull**; per-branch current roughly equal.
- Record: input V, output V, total A, per-branch A, voltage at the last branch, driver temperature.

## Cost ledger rules — proven

- **Toman only.** If a row looks 10× off, show the recorded value **and** the plausible value and
  ask. Never silently rewrite the user's number.
- Every row: date, item, qty, **unit price**, total, category, source, link, status.
- **Pack yield:** `units per pack = pack qty ÷ qty per unit`; `per-unit share = pack price ÷ units
  per pack`. Solder, heat-shrink, headers and TTP223 packs cover many units.
- **First unit vs batch:** the first unit carries tools and full packs; only the batch number is
  useful for pricing a product.
- **Missing rows are a finding.** Print, plexi, diffuser, packaging and bazaar purchases are the
  usual gaps.
- Run `scripts/ledger_check.py` to sum price columns and flag outliers.

## Journal vs BOM — proven

Keep them as two files, linked:

- **BOM / project file** — what to buy, specs, prices, order status.
- **Journal** — dated entries: goal → action → result → decision; plus current state, decisions,
  next steps, open questions, lessons.

The BOM answers "what do I buy"; the journal answers "why did I choose this and what happened".
Merging them makes both harder to use.

---

# Project-specific learnings

Project-specific facts do not belong in this file. Store them in
`references/projects/<project>-<YYYY-MM>.md` and link them from the project's own file. Promote a
fact to this file only when it is true beyond that one project — a platform rule, a component
limit, a price benchmark, or a measurement target.

For the Shadow Box, see `references/projects/shadow-box-2026-10.md`.
