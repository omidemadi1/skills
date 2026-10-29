# Project: {PROJECT_NAME}

> Created: {DATE} · Revision: V{N}
> Status: Brief | Risk Gate | Design | Sourcing | Wave 0 | Wave 1 | Wave 2 | Building | Testing | Done
> Definition of done: {one testable sentence}

---

## 1. Product Details

| Detail | Value |
|---|---|
| Type | {PRODUCT_TYPE} |
| Outer dimensions | {W×H×D} |
| Inner dimensions | {W×H×D} |
| Environment | Indoor / Outdoor / Humid / Hot |
| Primary material | {MATERIAL + thickness/grade} |
| Power | {source, voltage, current, connector} |
| Control | {switch / touch / remote / none} |
| Duty cycle | {continuous / minutes per day} |
| Use | Personal / Gift / For sale |
| Quantity | {1 / batch size} |
| Existing tools | {list or "see learnings"} |
| Notes | {constraints, references, inspiration} |

---

## 2. Definition of Done

> Write the pass condition before the BOM. If it cannot be tested, rewrite it.

- [ ] {functional criterion — e.g. "white areas glow evenly, no hotspot at 30cm"}
- [ ] {electrical criterion — e.g. "5V/2A input, driver <60°C after 10 min"}
- [ ] {mechanical criterion — e.g. "opens without desoldering; panel flush ±1mm"}
- [ ] {finish criterion — e.g. "no glue squeeze-out, no scratches"}
- [ ] {commercial criterion, if sold — e.g. "≤1.2M material cost at 50 units"}

---

## 3. Risk Register & Spikes

> Top assumptions that could kill the project. Score 1–3. Do not release the full BOM until the
> highest-risk spike passes or has a proven fallback.

| # | Assumption | L | I | Score | Spike (cheapest test) | Cost | Pass condition | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | {assumption} | 2 | 3 | 6 | {test} | {cost} | {pass} | ⬜ |
| 2 | {assumption} | 1 | 3 | 3 | {test} | {cost} | {pass} | ⬜ |

**Gate decision:** ⬜ Go / ⬜ No-go — {reason}

---

## 4. Design Review

### 4a. Power budget

| Load | V | A/unit | Qty | Total A | Total W | Notes |
|---|---|---|---|---|---|---|
| {load} | | | | | | |
| **Total** | | | | **{A}** | **{W}** | |

- Supply: {model / rating} · derating: {load ÷ rating}
- Voltage drop at last branch: {V} ({%)}
- Fuse: {rating}
- Connector: {type, size, current rating}
- **Verdict:** ⬜ OK / ⬜ Change design

### 4b. Thermal budget

| Heat source | Power | Location | Expected temp | Neighbour service temp | Verdict |
|---|---|---|---|---|---|
| {driver} | {W} | {place} | {°C} | {°C} | ⬜ |
| {LED strip} | {W/m} | {cavity} | {°C} | {°C} | ⬜ |

### 4c. Mechanical stack-up

```
back panel | wiring | LED | standoff | diffuser | print | front | frame
   {mm}    |  {mm} | {mm}|   {mm}  |   {mm}  | {mm}  | {mm}  | {mm}
```

- Inner depth available: {mm} · stack total: {mm} · clearance: {mm}
- Service access: {how it opens}
- Strain relief: {method}

### 4d. Interface check

| Connection | V | A | Connector | Polarity | Logic level | Match? |
|---|---|---|---|---|---|---|
| {source → driver} | | | | | | ⬜ |
| {driver → strip} | | | | | | ⬜ |
| {switch → load} | | | | | | ⬜ |

### 4e. Optical / finish

- CCT: {K} · CRI: {value}
- Diffuser: {type, thickness, standoff}
- Print: {paper, finish, size}
- Finish: {paint/coating, sheen}

### 4f. Safety

- [ ] Fuse on supply
- [ ] Strain relief on every exit cable
- [ ] Heat-shrink on every joint
- [ ] No mains inside a handmade enclosure
- [ ] Insulated PCB back / no exposed strands

---

## 5. Alternatives & Substitution Ladder

> For each critical choice: primary, fallback, avoid, and the trigger that tells you to switch.
> Read `references/component-playbooks.md` for the default ladders.

### {Category — e.g. Power path}

| Option | Role | Pros | Cons | Price | Choose when |
|---|---|---|---|---|---|
| {A} | **Primary** | | | | default |
| {B} | Fallback | | | | A unavailable/over budget |
| {C} | **Avoid** | | | | never for this load |

**Switch trigger:** {measurable condition}
**Decision:** {chosen option + one-line reason} · **Date:** {date}

### {Category — e.g. LED / diffuser / adhesive / joining}

| Option | Role | Pros | Cons | Price | Choose when |
|---|---|---|---|---|---|
| | Primary | | | | |
| | Fallback | | | | |
| | Avoid | | | | |

**Switch trigger:** {condition}
**Decision:** {chosen} · **Date:** {date}

---

## 6. Shopping List

### Raw materials (per unit)

| # | Item (EN) | آیتم (FA) | Specs | Qty | Unit price | Total | Link | Site | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | {thickness/size/grade} | | | | | | ⬜ |

### Components (per unit)

| # | Item (EN) | آیتم (FA) | Specs (V/A/size) | Qty | Unit price | Total | Link | Site | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | ⬜ |

### Tools (one-time)

| # | Item (EN) | آیتم (FA) | Capability needed | Qty | Unit price | Total | Link | Site | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | {e.g. temp-controlled 350°C} | | | | | | ⬜ |

### Consumables (with pack yield)

| # | Item (EN) | آیتم (FA) | Pack qty | Use per unit | Units per pack | Per-unit share | Link | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | ⬜ |

### Packaging & presentation

| # | Item | Specs | Qty | Unit price | Total | Link | Status |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | ⬜ |

### Still missing / not priced

| Item | Why missing | Next step |
|---|---|---|
| | | ⬜ |

---

## 7. Cost Summary

### One-time (tools, setup, templates)

| Item | Price | Notes |
|---|---|---|
| | | |
| **Total** | **{total}** | |

### Per unit

| Category | First unit | Unit 2+ | Notes |
|---|---|---|---|
| Raw materials | | | |
| Components | | | |
| Consumables (share) | | | |
| Packaging | | | |
| Labor | | | {hours × rate} |
| **Total** | **{first}** | **{next}** | |

### Effective cost at scale

| Quantity | Tools amortized | Material/unit | Total/unit |
|---|---|---|---|
| 1 | {all} | {unit} | {total} |
| 10 | {tools/10} | {unit} | {total} |
| 50 | {tools/50} | {unit} | {total} |
| 100 | {tools/100} | {unit} | {total} |

### Retail price & margin (if sold)

| | Plain | Professional |
|---|---|---|
| Cost/unit | | |
| Suggested retail | | |
| Gross margin | | |

> ⚠️ Ledger check: `python scripts/ledger_check.py {this-file}.md`

---

## 8. Buy Waves

| Wave | Items | Purpose | Status | Date |
|---|---|---|---|---|
| **0 — Spike** | {cheapest test parts} | Prove the riskiest assumption | ⬜ | |
| **1 — Core** | {structure, power, control} | Build the real thing | ⬜ | |
| **2 — Finish** | {diffusion, paint, packaging} | Complete and ship | ⬜ | |

> Do not release Wave 1 until Wave 0 passes. Wave 2 depends on final dimensions.

---

## 9. Build Guide

> Every step ends with an acceptance test. If a step has no test, it is not a step.

### Phase A — Prepare

1. {step} · **Test:** {pass condition}
2. {step} · **Test:** {pass condition}

### Phase B — Structure

1. {step} · **Test:** {pass condition}

### Phase C — Power & control

1. {step} · **Test:** {pass condition}

### Phase D — Optics & finish

1. {step} · **Test:** {pass condition}

### Phase E — Assemble & close

1. {step} · **Test:** {pass condition}

### Phase F — Pack

1. {step} · **Test:** {pass condition}

---

## 10. Measurement Log

| Quantity | Target | Measured | Conditions | Date |
|---|---|---|---|---|
| Input voltage | {V} | | charger: | |
| Output voltage | {V} | | load: | |
| Total current | {A} | | segments: | |
| Per-branch current | {A} | | branch: | |
| Voltage at last branch | {V} | | vs first: | |
| Driver temperature | <60°C | | after 10 min: | |
| Runtime before stable | 30 min | | | |
| Build time | {h} | | per phase: | |

**Actual vs estimate:** {what differed and why}

---

## 11. Order Sheet (per platform)

> Status: 🛒 در سبد · ✅ در حال خریداری · ⬜ تهیه نشده. Update the moment a cart changes.
> Payment is always the user's.

### 🛒 {Platform A} — {N} items

| # | Item | Price | Link | Status |
|---|---|---|---|---|
| 1 | | | | 🛒 |
| | **List total** | **{total}** | **Payable: {payable}** | |

> ⚠️ {platform trap}

### 🛒 {Platform B} — {N} items

| # | Item | Price | Link | Status |
|---|---|---|---|---|
| 1 | | | | 🛒 |

### ⬜ Still not in any cart

| Item | Price | Source | Next step |
|---|---|---|---|
| | | | |

---

## 12. Price Check History

| Date | Item | Old price | New price | Change | Action |
|---|---|---|---|---|---|
| | | | | | |

---

## 13. Feedback / Post-mortem

> **Where a lesson goes:** project-specific → `references/projects/<project>-<YYYY-MM>.md`;
> reusable across projects → `references/learnings.md`; changes the process → the skill itself.

### What worked

- {item/decision and why}

### What failed

| Symptom | Root cause | Fix | Rule added | Recorded in |
|---|---|---|---|---|
| | | | | projects / learnings / journal / skill |

### What cost more than expected

| Item | Estimate | Actual | Why |
|---|---|---|---|
| | | | |

### What I would do differently

1. {lesson}
2. {lesson}

### Next revision

- [ ] {change}
- [ ] {change}
