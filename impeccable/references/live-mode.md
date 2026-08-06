# Live Mode

Iterate on UI in the browser — pick an element, drop a comment, get three variants, accept one into source.

**Status:** Alpha. Works end-to-end, ready to try, rough edges on uncommon setups.

## When to Use

- Exploring directions on a real element (hero, newsletter card, pricing tier)
- Polishing a piece of UI that is almost right ("more playful", "less SaaS")
- Quick A/B between two directions your team is debating

**NOT for:** new greenfield features or whole-page redesigns — use `/impeccable` directly.

## How It Works

1. `/impeccable live` opens a picker overlay on your running dev server
2. Pick any element on the page
3. Context bar appears — type freeform description or pick action chip (bolder, quieter, distill, polish, typeset, colorize, layout, animate, delight, overdrive)
4. Optionally drop comment pins or draw strokes on the element first
5. Hit Go — 3 production-quality variants generated, each anchored to a genuinely different design archetype (not three riffs on color)
6. Variants hot-swapped via framework HMR
7. Cycle with arrow keys. Accept one → writes to source. Discard all → original stays

## Supported Frameworks

Vite, Next.js (including monorepos), SvelteKit, Astro, Nuxt, plain static HTML.

## CSP Handling

If dev server has strict Content Security Policy, first-run setup detects it and offers a one-time dev-only patch so the picker can load.

## Context Files

- `DESIGN.md` wins on visual decisions
- `PRODUCT.md` wins on voice
- With both, variants stay on-brand without being told

## Stopping

Say "stop live mode", close the tab, or hit exit button on picker bar.

## Pitfalls

- **Half-written pages** — variant generation needs context. Placeholder copy → generic variants. Fill content first
- **Macro decisions** — Live iterates on single elements. "Redo the entire pricing page" → use `/impeccable` directly
- **Generated files** — if element is in build output, picker says so and offers to route accept into true source. Don't force accept into generated file
- **Missing context files** — variants lean toward generic defaults without PRODUCT.md or DESIGN.md
- **Complex CSS frameworks** — some setups may need manual config. Check docs for framework-specific notes
