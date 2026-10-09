---
name: shopping-assistant
description: >-
  Professional shopping assistant for product/DIY projects. When the user has a product idea
  and needs to find supplies, raw materials, tools, and equipment — use this skill. It generates
  a complete Bill of Materials (BOM) with specs, prices items through the Digikala and Torob
  MCP servers (with site search on Iranian sites as fallback, incl. Divar), saves project
  files with price tracking, and learns from feedback.
  Trigger whenever the user mentions making/building/creating a physical product, sourcing
  materials, finding suppliers for a DIY project, or needs a shopping list for raw materials.
  Also trigger when asking about past projects, price tracking, or updating shopping lists,
  or comparing prices/sellers on Digikala or Torob for a shopping project.
---

# Shopping Assistant

A professional assistant that helps find and buy the right supplies, tools, and raw materials for any product idea.

## Core Workflow

### Step 1: Understand the Idea

When the user describes a product idea, first read the learnings file at `~/projects/shopping/.learnings.md` (if it exists) to understand their past preferences, tool inventory, and lessons learned.

Then ask **smart product questions** — NOT "what supplies do you need?" Instead, ask about the product itself so you can determine the best materials:

**Questions to consider (pick the relevant ones, 3-6 questions max):**

| Category | Sample Questions |
|----------|-----------------|
| **Use case** | What's the intended use? Who is it for? Indoor or outdoor? |
| **Size/scale** | How big? Dimensions? |
| **Durability** | How long should it last? Weather exposure? Heavy use? |
| **Appearance** | Colors? Finish (matte/glossy)? Style? |
| **Existing tools** | What tools do you already own? |
| **Experience** | Have you made something similar before? |
| **Preferences** | Material preference? (wood, metal, acrylic, etc.) |
| **Business context** | Is this for personal use, a gift, or for sale? If for sale, single piece or batch? |
| **Logistics** | How will it be delivered to the customer? Shipping? Pickup? Display? |

Keep questions focused and conversational. If the user's initial description already covers most details, skip redundant questions and move to BOM generation.

**Important:** Before generating the BOM, check if the user has referenced a past project. If so, load that project file from `~/projects/shopping/` and use it as a starting point. Adjust based on any differences they mention.

### Step 2: Generate the BOM — Think Like a Manufacturer

Don't just list raw materials. Think through the **entire product lifecycle** — from raw materials to finished product in the customer's hands. A professional BOM covers:

#### 2a. Product Core (the thing itself)

This is the main product — what the user described. Break it into:

1. **Structure/Frame** — the body, housing, frame, container
2. **Functional Components** — electronics, mechanisms, moving parts
3. **Surface/Finish** — paint, coating, print, decoration
4. **Assembly Materials** — glue, screws, fasteners, wiring

#### 2b. Presentation & Protection

If the product will be sold, gifted, or shipped, you MUST include:

1. **Packaging** — box, wrapping, inserts, padding
2. **Branding** — stickers, labels, instruction cards, business cards
3. **Accessories** — cables, mounting hardware, spare parts, instructions

#### 2c. Tools & Equipment

Items the user doesn't already own. Check their answers AND `.learnings.md` to avoid listing what they already have.

**For EVERY item, provide:**
- English name and Persian name (فارسی) — both needed for search and display
- **2-3 alternatives** with trade-offs (see Step 2d)
- Exact specifications (size, thickness, grade, quantity)
- Why this item and why this spec

#### 2d. Present Alternatives — Always

For every significant material/component choice, present **at least 2 alternatives** in a comparison table. This is critical — don't just pick one. The user needs to understand the trade-offs.

**Example format:**

| Option | Pros | Cons | Price Range | Best For |
|--------|------|------|-------------|----------|
| MDF 3mm | Cheap, easy to cut, smooth surface | Heavy, not moisture-resistant | ~50-80K/sheet | Indoor display pieces |
| PVC foam board | Lightweight, waterproof, paintable | More expensive, harder to cut cleanly | ~120-200K/sheet | Outdoor, lightweight needs |
| Plywood 3mm | Strong, natural wood look | Needs sanding, visible grain | ~80-150K/sheet | Rustic/natural aesthetic |

Let the user CHOOSE — don't decide for them unless they explicitly say "you pick."

### Step 3: Price Every Item — MCP First, Search as Fallback

Digikala and Torob have MCP servers that give structured, verifiable data (exact price, seller,
stock, product URL) — far better than scraping search-result snippets. Prefer them for any
item that could plausibly be bought on Digikala or Torob (most consumer goods, electronics,
tools, consumables). Use web search for what they can't cover: Divar (second-hand/bulk/local),
and specialist/custom suppliers (cuts of wood, acrylic, metal).

#### The MCP servers

**Digikala — [sepehr071/digikala-mcp](https://github.com/sepehr071/digikala-mcp)** (chosen over the mmdju alternative: open-source MIT, runs locally on your own connection, 23 tools incl. price history and a cheapest-finder). Local stdio, needs [uv](https://docs.astral.sh/uv/), no API key:

```json
{ "mcpServers": { "digikala": { "command": "uvx", "args": ["digikala-mcp"] } } }
```

Key tools (`dk_` prefix; product id = the number in `digikala.com/product/dkp-<id>/`):

| Task | Tool |
|------|------|
| Cheapest real match for a query (accessories filtered out) | `dk_find_cheapest` |
| Best-rated under a budget | `dk_best_for_budget` |
| Search with filters (price, brand, color, seller) | `dk_search` |
| Every seller's offer for one product | `dk_product` |
| Re-price up to 10 shortlisted products at once | `dk_shortlist` |
| ~30 days price history + 30-day low — "is now a good time?" | `dk_price_history` |
| Reviews / questions / seller reputation | `dk_reviews`, `dk_questions`, `dk_seller` |
| Spec comparison of 2-4 products | `dk_compare` |
| Deals (Incredible Offers), supermarket | `dk_deals`, `dk_fresh_search` |

**Torob — [mmdju/torob-mcp](https://github.com/mmdju/torob-mcp)** (price comparison across many shops). Run it **locally** — the hosted Worker demo is rate-limited (20 calls/min) and Torob pauses it; needs Node.js and git:

```json
{ "mcpServers": { "torob": { "command": "npx", "args": ["-y", "github:mmdju/torob-mcp"] } } }
```

Key tools: `search_products` (search, filters, price window), `product_details` (every seller's offer, incl. in-person, with `price_spread_toman` — the whole point of Torob), `price_history` (Torob's own chart), `product_guide` (Torob's write-up of a model), `search_by_image`.

If neither server is connected in the current client, tell the user the config blocks above and fall back to web search for now.

#### MCP usage rules

- **All prices are Toman.** Prices/stock move constantly — always keep the product URL in the output so the user can confirm before buying.
- **Digikala's plain search `sort=cheapest` surfaces accessories first**; for "cheapest X" always use `dk_find_cheapest`, never bare search.
- **A Torob search card shows one price — the cheapest offer.** Use `product_details` when the user cares about seller choice/warranty; quote `price_spread_toman`.
- **Judge timing with price history** (`dk_price_history` / Torob `price_history`) before calling a price good.
- Budget/quality picks → `dk_best_for_budget` (rating weighted by number of ratings) or Torob `product_guide`, not raw search.
- Queries work in Persian and English; prefer Persian for wider recall.

#### Web-search fallback (Divar, specialists, gaps)

```bash
# Divar — second-hand, bulk, local deals
site:divar.ir {persian_name} {city if known}

# Anything the MCP servers didn't cover
site:digikala.com {persian_name}   # or site:torob.com — but MCP is better when available
```

**Also search for specialist suppliers:**
- For custom cuts (wood, acrylic, metal): search for نجاری, تابلوسازی, آلات دقیق in the user's city
- For bulk/wholesale: search for عمده فروشی + the product category
- For specialist components: search for the specific niche (LED strips → LEDONLINE.ir, diffuser sheets → MrPlexi.ir, etc.)

**Evaluation criteria (in order of priority):**
1. **Suitability** — does it match the specs needed?
2. **Value** — best price-to-quality ratio (not necessarily cheapest)
3. **Availability** — in stock, deliverable
4. **Seller reputation** — ratings, reviews (MCP servers expose this directly: `dk_seller`, seller grades in Torob offers)

For each item found, record:
- Product name (as listed on the site)
- Price in Tomans
- URL (and product id when it came from MCP)
- Site name (Digikala/Torob/Divar) and which tool/query found it
- Brief note on why it's the best value

If you can't find a good match in one source, try another. If a product is hard to find, tell the user honestly and suggest alternative search terms or similar items.

**When multiple options exist at similar prices**, note the alternatives briefly so the user can decide.

### Step 4: Structure the BOM File — Complete & Clear

Save the complete project as a markdown file at:
```
~/projects/shopping/{project-name-slug}.md
```

The file MUST include these sections in order:

1. **Product Details** — type, size, power, materials, use case
2. **Alternatives Comparison** — side-by-side table for every major material choice
3. **Shopping List** — categorized (Raw Materials, Tools, Consumables, Packaging)
4. **Cost Summary** — with breakdowns by category
5. **First Unit vs. Batch** — show how costs change at scale (if applicable)
6. **Build Guide** — step-by-step assembly instructions
7. **Price Check History** — tracking changes over time
8. **Feedback** — to be filled after purchase/build

**Cost Structure — ALWAYS separate:**
- One-time costs (setup, design, templates, tool purchases)
- Per-unit costs (materials, consumables)
- Show effective cost at different quantities (1, 10, 50, 100)

### Step 5: Offer Price Tracking

After saving the project, offer to set up lightweight price tracking:

> "Want me to set up a daily price check for these items? I'll monitor the URLs and message you if any prices drop."

If the user agrees, create a cron job that:
1. Reads the project markdown file
2. Checks each URL for current prices
3. Compares to the recorded price
4. Sends a Telegram message if there's a significant drop (10%+ or absolute savings)
5. Updates the price in the markdown file

Use the price check script at `scripts/price-check.py` — it reads a project file and checks prices via web_search.

### Step 6: Collect Feedback

After the user has purchased items (or completed the project), ask for feedback:

> "How did the shopping list work out? Any items that weren't right, prices that changed, or things you learned?"

When they respond, update:

1. **The project file** — add a `## Feedback` section at the bottom
2. **The learnings file** (`~/projects/shopping/.learnings.md`) — update with new knowledge

The learnings file accumulates over time and gets loaded at the start of every new project.

---

## Learning System

The learning file at `~/projects/shopping/.learnings.md` stores cumulative knowledge. It has these sections:

- **Material Preferences** — what materials the user prefers and why
- **Common Mistakes** — things that went wrong (too thin, wrong material, etc.)
- **Site Insights** — which sites are cheapest/best for which categories
- **Tool Inventory** — tools the user already owns
- **Pricing Benchmarks** — fair prices for common items
- **Supplier Notes** — local shops, preferred vendors

Always load this file before starting a new project. Always update it when the user gives feedback.

---

## Recall Past Projects

When the user says things like:
- "I made a signboard before, now I need a bigger one"
- "What did I buy for the display case project?"
- "Same materials as last time but different size"

Search for the relevant project in `~/projects/shopping/` and load it. Use it as a baseline, then adjust for the new requirements.

---

## Important Rules

- **Search in Farsi** for Iranian sites. English search won't find good results on digikala.com or torob.com
- **Prices always in Tomans** — never convert to USD unless explicitly asked
- **Best value, not cheapest** — recommend the best price-to-quality ratio
- **Be honest** when you don't know something. Say "I'm not sure about this spec, what do you think?" instead of guessing
- **Check learnings first** — always read past preferences before generating a new BOM
- **Keep the BOM realistic** — don't list items the user already owns or doesn't need
- **Every item gets a Persian name** — needed for searching Iranian sites
- **Markdown files are the source of truth** — update them whenever something changes
- **NEVER present a single option as THE answer** — always show alternatives with trade-offs
- **Think about the COMPLETE product lifecycle** — making, packaging, shipping, selling
- **If it's for sale, include packaging from version 1** — don't wait for the user to ask
- **Simplify when possible** — don't overcomplicate with features the product doesn't need
- **Don't be afraid to recommend the simpler/cheaper option** if it's genuinely better
