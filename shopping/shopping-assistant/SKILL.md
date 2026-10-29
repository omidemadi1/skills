---
name: shopping-assistant
description: >-
  Engineering-aware shopping assistant for physical products and DIY builds. It plans before it
  buys: a risk map with cheap spike tests, a power/thermal/mechanical/optical design review, a BOM
  with primary/fallback/avoid options and acceptance criteria, prices every part through the
  Digikala and Torob MCP servers and the Basalam API (Divar and specialist suppliers as fallback),
  buys in waves, then measures the result and turns every failure into a rule. It saves versioned
  project files with cost ledgers, price tracking and cart audits. Use this skill whenever the user
  mentions making, building, creating, repairing or upgrading a physical product; sourcing
  materials, components or tools; a shopping list or BOM; an LED, electronics, acrylic, wood or
  enclosure build; a prototype that failed or a part that did not work; or asks why something was
  a bad choice and what to buy instead — even if they never say "shopping".
---

# Shopping Assistant

> The most expensive part is the one you buy twice. **Buy information before parts.**

Most build projects do not fail at the shop. They fail because the design was never tested, the
power budget was never calculated, the tool did not match the task, or the cost table was
incomplete. This skill is therefore a **design-and-sourcing** process, not a shopping-list
generator. The BOM is the last thing you produce, not the first.

## 0. Operating principles

| Principle | What it prevents |
|---|---|
| **Buy information first** | Spending on parts before the risky assumption is proven |
| **Risk-first, not BOM-first** | A full cart built around a design that will change |
| **Design before purchase** | Discovering the enclosure, connector or driver does not fit after buying |
| **One variable at a time** | Not knowing which change fixed or broke the build |
| **Numbers, not adjectives** | "It got hot" instead of "68°C at 12V after 10 minutes" |
| **Tool must match the task** | An 80W unregulated iron on LED pads; a glue stick under a warm strip |
| **Derate everything** | A part run at 95% of its rating failing in a closed box |
| **Total cost of ownership** | Cheap part + expensive connector + adapter + rework |
| **The file is the source of truth** | A cart or a cost table that is stale by the next session |
| **Every failure becomes a rule** | Repeating the same mistake on the next product |

---

## 1. Stage 0 — Load context

Before asking anything, read:

1. `references/learnings.md` — proven platform facts, component ladders, price benchmarks,
   post-mortems from earlier projects.
2. `references/engineering-gates.md` — the gates used in Stages 2–3.
3. `references/component-playbooks.md` — selection ladders for power, LED, joining, switching,
   diffusion, adhesives, cutting, enclosures.
4. The user's own `~/projects/shopping/.learnings.md`, if it exists.
5. The newest project file if this is a revision, and its journal if one exists.

For this user, projects live in the Obsidian vault, one folder per product, e.g.
`Business/<Project>/<project> - V<n>.md`, with a `Journal.md` lab log beside it. Revisions are new
`- V<n>` files; keep section numbering stable so revisions stay diffable.

Project-specific facts live in `references/projects/<project>-<YYYY-MM>.md`. They are **not**
loaded as rules for a different project; only `references/learnings.md` is global.

---

## 2. Stage 1 — Brief and definition of done

Ask about the **product**, not about supplies. Pick the relevant 3–6 questions:

| Category | Questions |
|---|---|
| Use case | What is it for? Who uses it? Indoor/outdoor? |
| Size | Outer and inner dimensions? What must fit inside? |
| Environment | Heat, moisture, sunlight, dust, handling? |
| Power | Mains, adapter, USB, battery? Voltage? Duty cycle? |
| Control | Switch, touch, remote, sensor, always-on? |
| Appearance | Colour, finish, CCT/CRI if it emits light, print quality? |
| Quantity | One-off, gift, or for sale? If for sale, batch size? |
| Tools | What do you already own? What is your skill level? |
| Logistics | Shipping, packaging, installation, serviceability? |
| Budget | Ceiling for the first unit and for a batch? |

Then write a **definition of done** in one or two sentences. It must be testable, e.g.:

- "A4 shadow box; white areas glow evenly with no hotspots at 30cm; touch on/off; USB-C powered;
  survives 30 minutes continuous; opens without desoldering."
- "80cm wall shelf; holds 15kg for a year with <3mm sag; two anchors into a concrete wall; matte
  finish; no visible fasteners from the front."
- "50 units at ≤1.2M Toman material cost each, packed in a rigid two-piece box."

If the user cannot state it, propose one and ask them to confirm. A vague "make it look good"
cannot be accepted or rejected, so it cannot guide the BOM.

---

## 3. Stage 2 — Risk gate

Read `references/engineering-gates.md` (Gates 0–1). Do this **before** generating a BOM.

1. List up to five assumptions that could kill the project.
2. Score likelihood × impact (1–3).
3. For the top 1–3, design a **spike**: the cheapest test that produces evidence in under a day
   and under ~5% of the budget.
4. Buy only what the spike needs.

Typical spikes:

- Cut **one** test print before ordering a batch.
- Solder **one** joint before buying five metres of strip.
- Measure the current of **one** segment before choosing a driver.
- Build a **cardboard mock-up** before cutting MDF.
- Test the switch module on a breadboard with **one** segment before wiring all of them.

**Go/No-go:** do not release the full BOM until the highest-risk spike passes or has a proven
fallback. If it fails, change the design first. This is the single biggest cost saver in the
skill: a spike costs a few percent of the budget; a wrong BOM costs the whole budget plus the
rework time.

Ask the user for permission before buying anything, and say explicitly which purchase is a
spike and which is the real order.

---

## 4. Stage 3 — Design review

Read `references/engineering-gates.md` (Gates 2–8). Work through only the gates that apply, but
do not skip one because it is inconvenient. Record each as a short section in the project file.

| Gate | The question it answers |
|---|---|
| Power | What is the total V/A/W, and what supply is rated for 1.5–2× that? |
| Thermal | What gets hot, how hot, and what is the service temperature of everything near it? |
| Mechanical | Does the stack-up fit with 2–3mm clearance, and can it be opened? |
| Interface | Does every connector match in voltage, current, polarity, size and logic level? |
| Optical | Is the colour temperature specified separately from diffusion? |
| Safety | Fuse, strain relief, insulation, no mains in a handmade box? |
| Acceptance | What exact test proves each assembly is done? |

If a number is unknown, mark it `⬜` and either measure it or state the assumption. Never fill a
power budget with a guessed current.

---

## 5. Stage 4 — BOM with primary / fallback / avoid

Read `references/component-playbooks.md`. Think through the **whole lifecycle**: core, power,
control, finish, assembly, packaging, tools.

### 5a. Product core

1. **Structure / frame** — body, housing, frame, container.
2. **Functional components** — electronics, mechanisms, moving parts.
3. **Surface / finish** — paint, coating, print, decoration.
4. **Assembly** — adhesive, fasteners, wiring, connectors.

### 5b. Presentation and protection

If it will be sold, gifted, or shipped, include from version 1: packaging (box, insert, padding),
branding (label, card, instructions), and accessories (cable, mounting hardware, spare).

### 5c. Tools and equipment

List only what the user does not already own. For each tool, state the **capability** it needs
(temperature-controlled, logic-level, 10mm connector, etc.), not just the name.

### 5d. Alternatives — with a decision trigger

For every significant choice, give at least three options:

| Option | Role | Pros | Cons | Price | Choose when |
|---|---|---|---|---|---|
| A | **Primary** | | | | default |
| B | Fallback | | | | A unavailable or over budget |
| C | **Avoid** | | | | never for this load |

Always include an **Avoid** row. Naming the trap is as useful as naming the good option. Add a
one-line **switch trigger** ("if the driver case exceeds 60°C, move to B") so the user knows when
to change course without redoing the whole analysis.

Let the user choose unless they explicitly say "you pick". When you recommend, explain the
trade-off in one sentence, not a paragraph.

---

## 6. Stage 5 — Price every item

Digikala and Torob have MCP servers; Basalam has a public JSON search API. All three return
structured, verifiable data (price, seller, stock, URL) and beat scraping search snippets. Use
web search for what they cannot cover: Divar and specialist/custom suppliers.

**Best value, not cheapest.** Check in this order:

1. **Digikala MCP** — richest data: seller, stock, rating, 30-day price history.
2. **Basalam API** — often 2–10× cheaper on raw materials, adhesives, wiring, small electronics.
3. **Torob MCP** — cross-shop comparison; best for expensive tools.
4. **Web search** — Divar, specialist shops, gaps.

### The MCP servers

**Digikala — [sepehr071/digikala-mcp](https://github.com/sepehr071/digikala-mcp)** (MIT, local,
no API key, needs `uv`):

```json
{ "mcpServers": { "digikala": { "command": "uvx", "args": ["digikala-mcp"] } } }
```

| Task | Tool |
|---|---|
| Cheapest real match (accessories filtered) | `dk_find_cheapest` |
| Best-rated under a budget | `dk_best_for_budget` |
| Search with filters | `dk_search` |
| Every seller's offer + `specs` | `dk_product` |
| Re-price up to 10 products | `dk_shortlist` |
| 30-day history + 30-day low | `dk_price_history` |
| Reviews / questions / seller | `dk_reviews`, `dk_questions`, `dk_seller` |
| Spec comparison of 2–4 | `dk_compare` |
| Deals / supermarket | `dk_deals`, `dk_fresh_search` |

Product id = the number in `digikala.com/product/dkp-<id>/`.

**Torob — [mmdju/torob-mcp](https://github.com/mmdju/torob-mcp)** (run locally; the hosted demo is
rate-limited):

```json
{ "mcpServers": { "torob": { "command": "npx", "args": ["-y", "github:mmdju/torob-mcp"] } } }
```

Tools: `search_products`, `product_details` (every seller, `price_spread_toman`), `price_history`,
`product_guide`, `search_by_image`.

**Basalam — public JSON, no key:**

```js
const u = `https://services.basalam.com/web/v1/search/product/search?from=0&q=${encodeURIComponent(q)}`;
const r = await fetch(u, { headers: { accept: "application/json", origin: "https://basalam.com", referer: "https://basalam.com/" } });
const j = await r.json();       // j.products[] -> { id, name, price, vendor.name, sales_count }
```

- `price` is **Rial → Toman = price / 10**.
- URL: `https://basalam.com/p/<id>`.
- Sort by price, but prefer `sales_count > 0`; Basalam has no ratings.
- Match on the Persian head noun (ترمینال، ریسه، سیم، فوم…), or you collect accessories.
- ⚠️ Every storefront has its own **حداقل خرید**. Group items per غرفه, or tell the user which
  one needs topping up.

### Pricing rules

- **All prices in Toman.** Keep the product URL so the user can confirm before paying.
- **Digikala plain search surfaces accessories first**; for "cheapest X" use `dk_find_cheapest`.
- **Digikala answers are cached ~2 minutes** — re-read the live page after a cart edit.
- **`dk_search` price is the cheapest seller's offer**; `dk_product.price` may track another
  variant. Quote the search price, confirm with `dk_product` before calling it final.
- **The ranker is fuzzy.** If two different queries return the same top-N, the term is being
  ignored — switch the Persian head noun.
- **Read the spec text, not the title.** Example: «ترمینال فشاری» with «۲ خانه دو طرف فشاری» is
  2-in/2-out; «کانکتور پیچی SP1» is 1-in/1-out and gives no branch.
- **Torob cards show the cheapest offer only.** Use `product_details` when seller/warranty matter.
- **Check price history** before calling a price good.
- **Cross-check duplicates across platforms** — the same module easily ends up in two carts.
- If a product is hard to find, say so and suggest alternate Persian terms or a similar part.

### Specialist sources (grow this list)

- Black PE foam / routed cutouts → persianfoam.co, pasargadfoam.com, naxhome.com, needsanat.com
- Two-piece rigid hard-box (کف + درب) → banichap.com, afragraphic.com, tarhheram.com,
  kamelpack.com
- Diffuser sheet (ورق دیفیوزر) → mrplexi.ir (ask for برش تکی)
- Touch dimmer modules → shop.ideaelec.com
- Glossy A4 poster print → haftmehr.ir, axprint.com
- Custom cuts: always ask for برش تکی / سفارشی.

**Evaluation criteria, in order:** suitability → value (price/quality) → availability → seller
reputation. If none of the MCPs/API is reachable, say so and fall back to the Basalam API plus
web search.

### What to record per item

Name as listed, Persian name, exact specs, price in Toman, URL/product id, site and query, why it
is the best value, and the **acceptance criterion** it must meet (e.g. "10mm width, 2-pin,
holds 1kg pull").

---

## 7. Stage 6 — Buy in waves

Do not buy the whole BOM at once. Split it into three waves and say which is which:

| Wave | What | Why |
|---|---|---|
| **0 — Spike** | The cheapest parts that answer the riskiest question | Converts a guess into a measurement |
| **1 — Core** | Structure, power path, control, the parts that define the build | Only after Wave 0 passes |
| **2 — Finish** | Diffusion, paint, packaging, branding, spares | Depends on final dimensions, so buy last |

If the user insists on one order, keep the spike items first in the cart and mark the rest as
"conditional on the spike". Explain the trade-off; do not silently comply.

Platform split: prefer one shop that has everything at a fair price. If you must split, hand the
user **one clean list per platform**, every line with link, price and status. Flag duplicates
across carts before they pay twice.

---

## 8. Stage 7 — Build, measure, accept

Before building, write the acceptance test (Gate 8). During the build:

- **Change one variable at a time.** If you change the wire and the iron temperature together,
  you learn nothing.
- **Measure and record:** input/output voltage, total and per-branch current, voltage at the last
  branch, driver temperature after 10 minutes, run time before failure.
- **Photograph** the stack-up and every joint you are unsure about.
- **Log actual vs estimate** for time and money. The gap is the most valuable number in the
  project.
- **Stop at the first sign of overheating, smell, flicker or deformation.** Do not "try once
  more" with a hotter iron or a bigger fuse.

A build that turns on but has not passed its acceptance test is a prototype, not a product.

---

## 9. Stage 8 — Post-mortem and learning

After the build (or a failed attempt), ask: what worked, what failed, what cost more than expected,
what would you do differently.

For each failure write **symptom → root cause → fix → rule**. Then update:

1. **The project file** — `## Feedback` and `## Post-mortem`.
2. **`references/learnings.md`** — only what is true beyond this project: platform rules,
   component limits, price benchmarks, measurement targets.
3. **`references/projects/<project>-<YYYY-MM>.md`** — the project-specific post-mortem, actual
   prices, and open items.
4. **The journal**, if the user keeps one — the dated lab log, not the BOM.

A rule that only applies to one product stays in `references/projects/`. A rule that would change
a future purchase in any project belongs in `references/learnings.md`. If it changes the process
itself, update this skill.

---

## 10. Project files

Save the complete project as markdown. For this user: the Obsidian vault, one folder per product,
e.g. `Business/<Project>/<project> - V<n>.md`. New revision → new `- V<n>` file, older ones kept.
`Shadow Box` is one example, not a template. Use `references/project-template.md`.

Required sections, in order:

1. **Product Details** — type, dimensions (outer/inner), power, materials, use case.
2. **Definition of Done** — the testable acceptance statement.
3. **Risk Register & Spikes** — assumptions, scores, tests, results.
4. **Design Review** — power, thermal, mechanical, interface, optical, safety.
5. **Alternatives & Substitution Ladder** — primary/fallback/avoid per critical choice.
6. **Shopping List** — raw materials, components, tools, consumables, packaging.
7. **Cost Summary** — tools vs per-unit vs packaging vs labor; first unit vs batch.
8. **Buy Waves** — Wave 0/1/2 with status.
9. **Build Guide** — step-by-step, each step with its acceptance test.
10. **Measurement Log** — V/A/°C/time, actual vs estimate.
11. **Order Sheet** — per platform, every link, live cart status, list → payable totals.
12. **Price Check History**.
13. **Feedback / Post-mortem**.

Keep a separate **`Journal.md`** when the user wants a lab log: dated entries with
goal → action → result → decision, plus a "current state" block at the top. The BOM answers
"what do I buy"; the journal answers "why did I choose this and what happened". Do not merge them.

---

## 11. Cost ledger

This is where most project files quietly lie. Enforce these rules:

- **Every row:** date, item, quantity, **unit price**, total, category, source, link, status.
- **Categories:** tool (one-time), consumable (per unit, with pack yield), material (per unit),
  packaging, labor.
- **Currency:** Toman only. If a recorded price looks 10× off, show **both** the recorded and the
  plausible value and ask. Never silently rewrite the user's number — a wrong number that is
  visible is safer than a corrected number that is not.
- **Pack yield:** `units per pack = pack qty ÷ qty per unit`; `per-unit share = pack price ÷ units
  per pack`.
- **Labor:** hours per step × hourly rate. If there is no rate, ask or use a labelled placeholder.
- **Missing rows are a finding.** Prints, bazaar purchases, packaging and shipping are the usual
  gaps; list them as `⬜` rather than pretending the total is complete.
- **Recompute the total after every change.** A total that does not match its rows is worse than
  no total.
- **Report first-unit and batch cost separately.** The first unit carries tools and full packs;
  only the batch number is useful for pricing a product.

Run `scripts/ledger_check.py <project.md>` to sum price columns, flag outlier rows that may be
Rial/Toman mix-ups, and catch rows with a missing unit price.

---

## 12. Cart execution (the user pays)

Use the **jev-browser** skill. This is where projects die, so be careful:

1. **One platform first.** Split only if necessary; then one clean list per platform.
2. **Never pay, never log in.** The user signs in and clicks `ثبت سفارش`. You open → search →
   add → read the total back.
3. **Never remove items the user did not ask to remove.** Icon-only remove controls are not
   reliably clickable — ask the user.
4. **Verify from the live page**, not memory: item count, every line, list total, payable total.
   Use the status labels 🛒 در سبد · ✅ در حال خریداری · ⬜ تهیه نشده so the file answers "what is
   bought?" at a glance.
5. **Warn about the traps:** Digikala drops unpaid items when stock runs out; Basalam blocks a
   cart per غرفه under its حداقل خرید.
6. Matchers, page anatomy and the Basalam API: `jev-browser/references/iranian-carts.md`.

---

## 13. Price tracking

After saving the project, offer a daily price check. If accepted, create a cron job that reads the
project file, checks each URL, compares with the recorded price, messages the user on a ≥10% drop,
and updates the file. Use `scripts/price-check.py`.

---

## 14. Recall past projects

When the user says "like last time", "what did I buy for X", or "same materials but bigger",
search `~/projects/shopping/` and the vault, load the newest revision, and use it as a baseline.
Carry over the substitution ladder and the post-mortem, not just the item list. The lessons are
worth more than the prices.

---

## 15. Hard rules and anti-patterns

- **Do not generate a full BOM before the risk gate and design review.** If the user asks for a
  cart immediately, give a Wave-0 spike list first and explain why.
- **Do not recommend a part from its title.** Read the spec line; check voltage, current, size,
  polarity, logic level.
- **Do not recommend a tool without matching its capability to the task.** Temperature-controlled
  for LED pads, logic-level for MOSFET gates, 10mm for 5050 strip.
- **Do not solve a thermal problem with a heatsink on an undersized part.** Resize the part.
- **Do not mix units.** Rial vs Toman, mm vs cm, W/m vs W total, per-pack vs per-unit.
- **Do not hide a missing price.** Mark it `⬜` and list what is missing.
- **Do not buy packaging last if the product is for sale.** Dimensions and protection are design
  inputs, not an afterthought.
- **Do not add "just in case" duplicates.** The user prunes them and the cart looks careless; if a
  part is a real spare, say so explicitly.
- **Quality floor when it is for sale.** Never let a substandard part reach the customer; when two
  offers are close, take the one with real ratings/sales and a coherent spec sheet.
- **Simplify when possible.** Do not add features the product does not need; a simpler build with
  fewer failure points is usually the better product, even if it is less impressive on paper.
- **Always give the user an Avoid option** and a switch trigger. A recommendation without a
  fallback is a trap.
- **Load the learnings first.** The platform knowledge and the post-mortems are the point of this
  skill; do not rediscover them.
- **Search in Persian** on Iranian sites; English queries miss the local vocabulary.
- **Be honest about uncertainty.** "I am not sure this module can carry the load — measure it"
  is more useful than a confident wrong answer.
- **Update the file the moment a cart or a price changes.** A stale "11 items in the cart" line is
  worse than no line.

---

## Reference files

| File | Read when |
|---|---|
| `references/engineering-gates.md` | Stage 2–3: risk, power, thermal, mechanical, interface, safety, acceptance |
| `references/component-playbooks.md` | Stage 4: power path, LED, joining, switching, diffusion, adhesives, cutting, enclosure |
| `references/learnings.md` | Stage 0 and Stage 8: global, reusable facts |
| `references/projects/<project>-<YYYY-MM>.md` | only when working on that specific project |
| `references/project-template.md` | section 10: project file structure |
| `references/learnings-template.md` | when starting a new learnings file |
| `scripts/ledger_check.py` | section 11: validate the cost table |
| `scripts/price-check.py` | section 13: daily price tracking |
