# Engineering Gates — buy information before parts

> Read this at Stage 2 of the workflow. These gates exist because the expensive mistakes in a
> physical build are almost never "wrong supplier" — they are **wrong design, discovered after
> buying**. Each gate is a cheap question that prevents an expensive purchase.

## Contents

1. Gate 0 — Brief completeness
2. Gate 1 — Risk map and spike test
3. Gate 2 — Power budget
4. Gate 3 — Thermal budget
5. Gate 4 — Mechanical stack-up
6. Gate 5 — Interface compatibility
7. Gate 6 — Optical and finish
8. Gate 7 — Safety and serviceability
9. Gate 8 — Acceptance criteria
10. Gate 9 — Cost ledger completeness
11. Gate 10 — Post-build review
12. Templates

---

## Gate 0 — Brief completeness

Do not generate a BOM until these are known or explicitly assumed:

| Field | Why it changes the BOM |
|---|---|
| Use case and owner | Gift vs product vs prototype changes quality floor |
| Environment | Indoor/outdoor/humid/heat changes material and adhesive |
| Outer **and** inner dimensions | Drives material thickness, span, fit, shipping |
| Power source and voltage | Drives driver, connector, wire, safety |
| Control method | Mechanical switch vs touch vs remote vs none |
| Duty cycle | Continuous vs occasional changes thermal design |
| Quantity | 1 vs 50 changes process (hand cut vs laser, solder vs connector) |
| Definition of done | "Works" is not a spec; write the pass condition |
| Existing tools | Prevents re-buying and reveals capability gaps |
| Skill level | Determines whether a method is realistic |

If a field is unknown, mark it `⬜` and ask. **Do not invent a number to fill the table.**
An explicit unknown is safer than a confident guess.

---

## Gate 1 — Risk map and spike test

Before buying the full BOM, list the assumptions that could kill the build. Score each
likelihood × impact (1–3 each). For the top 1–3, design a **spike**: the cheapest test that
produces real evidence in under a day and under ~5% of the project budget.

| Risk | Likelihood | Impact | Spike | Cost | Pass condition |
|---|---|---|---|---|---|
| Example: hand-cut poster edges look clean | 2 | 3 | Cut one test print with a fresh blade | 1 print | No torn fibres at 30cm |
| Example: 5V→12V boost can run the strip | 3 | 3 | Measure current of one segment, then two | multimeter | Driver <60% rated, case <60°C |
| Example: touch module can switch the load | 2 | 3 | Breadboard TTP223 + MOSFET + one segment | ~100K | No flicker, MOSFET cool |

**Go/No-go:** release the full BOM only when the highest-risk spike has passed **or** has a
proven fallback. If the spike fails, change the design before buying anything else.

Why: a spike converts a guess into a measurement for a few percent of the budget. Buying the
whole BOM first converts the same guess into a sunk cost that biases every later decision.

---

## Gate 2 — Power budget

Fill this before choosing any driver, connector, or wire.

| Load | Voltage | Current per unit | Qty | Total current | Total power |
|---|---|---|---|---|---|
| LED segment A | 12 V | 0.24 A | 1 | 0.24 A | 2.9 W |
| LED segment B | 12 V | 0.24 A | 4 | 0.96 A | 11.5 W |
| **Total** | | | | **1.20 A** | **14.4 W** |

Rules:

- **Derate the supply.** Continuous rating ≥ 1.5–2× the load; aim to run at ≤50–60% of rating.
  A module that is "2A max" is not a 2A module in a closed box.
- **Boost converters:** `I_out ≈ I_in × (V_in / V_out) × efficiency` (use 0.85). Check the
  switch-current limit, not the marketing "2A". At 5V→12V, a 2A-switch module is only good for
  roughly 0.5–0.7A out, and it gets hot near that.
- **Buck/boost modules need headroom.** Read the datasheet: input range, switch current,
  efficiency curve, thermal resistance.
- **USB-C is not a 3A socket by default.** A dumb device needs 5.1kΩ from CC1 and CC2 to GND
  to get more than 0.5A from a USB-C charger. For 12V, use a **PD trigger** module, not a boost.
- **Voltage drop:** keep it under ~5% at the far end (0.6V at 12V, 0.25V at 5V). Short, thick
  conductors; measure at the last branch, not at the supply.
- **Fuse:** 1.5–2× the expected current, on the supply side.
- **Wire:** 0.5–0.75mm² is plenty for a few amps at 12V over a metre; the connector is usually
  the weak point, not the copper.

If the budget says "borderline", the design is wrong — choose a bigger driver, a lower-voltage
strip, or fewer/shorter segments. Do not solve a thermal problem with a heatsink on a module
that was never meant for the load.

---

## Gate 3 — Thermal budget

Heat decides whether adhesives, plastics, and hands survive.

- **LED strip:** 5050 12V at 60 LED/m is ~14.4W/m (1.2A/m). In a closed box, derate 20–30%.
- **Driver:** measure case temperature after 10 minutes at full load. Target <60°C.
- **Adhesive service temperature:** glue stick ~50°C; hot glue ~60–80°C; 3M VHB ~90°C+;
  neutral silicone ~200°C; epoxy ~120°C+.
- **Soldering:** LED pads tolerate ~300–350°C for 2–3 seconds. An unregulated 80W iron can
  exceed 400°C and delaminate the pad or melt the strip body.
- **Enclosed volume:** if there is no vent, assume the air will reach the driver case
  temperature. Put the driver where it can shed heat, or derate it.

If a component's temperature is unknown, measure it. "It felt warm" is not a thermal budget.

---

## Gate 4 — Mechanical stack-up

Draw a side view **before** cutting or wiring. Every layer needs a number:

```
back panel | wiring depth | LED height | standoff | diffuser | print | front acrylic | frame
```

Rules:

- **Enclosure before wiring.** Panel-mount connectors, cable exits, and service access are
  determined by the enclosure, not by the circuit.
- **Clearance:** allow 2–3mm between layers for tolerances, adhesive, and print thickness.
- **Standoff for diffusion:** 15–25mm between strip and diffuser is the usual working range;
  less gives hotspots, more loses brightness.
- **No load on solder joints.** Strain-relieve cables; the joint should never carry weight.
- **Material for span:** 3mm MDF/board is a prototype material; it warps. Use 6mm MDF,
  plywood, or a frame for a permanent piece.
- **Serviceability:** the unit should open without desoldering. Use a connector between the
  back panel and the strip harness.
- **Mock up in cardboard at full size.** Thirty minutes of cardboard prevents a re-cut.

---

## Gate 5 — Interface compatibility

For every connection, write down: voltage, current, polarity, connector type, gender, size,
and signal level. Most "it doesn't work" failures are one of these.

- **Logic cannot drive a load.** A TTP223 output sources a few mA; an LED strip needs hundreds.
  Use a logic-level MOSFET (e.g. AO3400), a relay, or a ready-made driver module.
- **Connector must match the physical part.** 8mm vs 10mm strip width; 2-pin vs 4-pin;
  panel thickness vs socket thread; wire gauge vs terminal range.
- **Polarity:** mark + and − on the strip and on the harness. Reverse polarity kills strips.
- **Signal vs power:** do not run a 12V load through a 3.3V logic pin, and do not assume a
  "touch module" is a switch — read whether the output is momentary or toggle.

---

## Gate 6 — Optical and finish

- **Diffusion is not colour.** A milky/opal diffuser evens out hotspots; it does not turn a
  warm-white strip into a cool-white one. Specify **CCT** (2700/3000/4000/6000–6500K) and
  **CRI** separately.
- **Each diffuser layer costs light** (roughly 10–15%). Two layers lose 15–25%. Use one good
  diffuser rather than milky acrylic + diffuser.
- **Evenness:** white reflective cavity behind the strip, consistent standoff, and avoid
  placing the strip closer than ~10mm to the diffuser.
- **Print:** glossy vs photo-glossy changes both colour and cut behaviour. Test-cut one print
  before committing a batch.
- **Finish:** matte vs gloss changes fingerprints and scratches; paint adhesion needs the
  right primer for the substrate.

---

## Gate 7 — Safety and serviceability

- Fuse and strain relief on every cable that leaves the enclosure.
- No mains voltage inside a handmade enclosure. If mains is unavoidable, use a certified
  driver and keep mains wiring physically separated and insulated.
- Heat-shrink every solder joint; no exposed strands.
- Insulate the back of any exposed PCB; avoid conductive adhesive near terminals.
- Design for repair: replaceable strip, accessible screws, labelled polarity.

---

## Gate 8 — Acceptance criteria

Write pass/fail **before** building. If you cannot test it, you cannot call it done.

| Assembly | Test | Pass condition |
|---|---|---|
| Solder joint | Pull test + continuity | Holds ~1kg for 10s; <1Ω |
| Power | Measure output, 10-min soak | Within ±5% of target; case <60°C |
| LED run | 30-min continuous | No flicker, no colour shift, no hot spot |
| Optics | View at 30cm | No visible hotspots; even illumination |
| Mechanics | Shake + fit check | No rattle; panel flush ±1mm |
| Finish | Visual | No glue squeeze-out, no scratches |

A build that "turns on" but has not passed its acceptance test is a prototype, not a product.

---

## Gate 9 — Cost ledger completeness

Every purchase needs: date, item, quantity, **unit price**, total, category, source, link,
status. Categories: tool (one-time), consumable (per unit, with pack yield), material
(per unit), packaging, labor.

- **Toman only.** If a number looks 10× off, show the recorded value and the plausible value
  side by side and ask — never silently rewrite the user's number.
- **Pack yield:** `units per pack = pack quantity ÷ quantity per unit`.
  `per-unit share = pack price ÷ units per pack`.
- **Labor:** hours per step × hourly rate. If the user has no rate, ask or use a placeholder.
- **First unit vs batch:** report both. The first unit carries the tools and full packs; the
  batch price is what matters for a product.
- **Missing rows are a finding.** Bazaar purchases, prints, and packaging are the usual gaps.

---

## Gate 10 — Post-build review

For every failure or surprise, write:

```markdown
### Symptom
What was observed (not interpreted).

### Root cause
The physical/electrical reason, verified if possible.

### Fix
What changed.

### Rule
The general rule this adds to `references/learnings.md`.
```

Then update the project file and the learnings file. If the rule is general enough to affect
future projects, update this skill's references too. That is how the skill gets better instead
of repeating the same mistake with a different product.

---

## Templates

### Risk register

| # | Assumption | Likelihood (1–3) | Impact (1–3) | Spike | Cost | Pass condition | Status |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | ⬜ |

### Power budget

| Load | V | A/unit | Qty | Total A | Total W | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

### Measurement log

| Quantity | Value | Conditions | Date |
|---|---|---|---|
| Input voltage | | Charger: | |
| Output voltage | | Load: | |
| Total current | | Segments: | |
| Per-branch current | | Branch: | |
| Voltage at last branch | | Compare to first: | |
| Driver temperature | | After 10 min: | |

### Acceptance test

| Test | Method | Pass condition | Result |
|---|---|---|---|
| | | | ⬜ |

### Post-mortem

| Symptom | Root cause | Fix | Rule added | Recorded in |
|---|---|---|---|---|
| | | | | |
