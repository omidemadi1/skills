# Anti-Slop Ban List

Complete list of patterns that make AI-generated frontends look the same. The agent enforces these on every output unless the brief explicitly asks for one.

## Visual & CSS Bans

- NO neon/outer glows. Use inner borders or subtle tinted shadows
- NO pure black (`#000000`). Off-black, zinc-950, or charcoal
- NO oversaturated accents. Desaturate to blend with neutrals
- NO excessive gradient text for large headers
- NO custom mouse cursors (outdated, a11y-hostile, perf-hostile)
- NO AI-purple and mesh blob gradients as default

## Typography Bans

- AVOID Inter as default (use Geist, Outfit, Cabinet Grotesk, Satoshi)
- NO oversized H1s that just scream. Control hierarchy with weight + color
- NO Fraunces or Instrument_Serif (LLM-favorite display serifs)
- NO mixed-family emphasis (random serif word in sans headline). Use italic/bold of same font

## Layout & Spacing Bans

- NO 3-column equal feature cards. Use 2-column zig-zag, asymmetric grid, scroll-pinned, or horizontal-scroll
- NO `border-t` + `border-b` on every row of long lists/spec tables
- NO mathematically perfect padding with awkward floating gaps
- NO split-header pattern ("left big headline + right small explainer paragraph")

## Content & Data Bans ("Jane Doe" Effect)

- NO generic names: "John Doe", "Sarah Chan", "Jack Su"
- NO generic avatars: SVG "egg" or Lucide user icons
- NO fake-perfect numbers: `99.99%`, `50%`, `1234567`. Use organic data: `47.2%`, `+1 (312) 847-1928`
- NO startup-slop brand names: "Acme", "Nexus", "SmartFlow", "Cloudly"
- NO filler verbs: "Elevate", "Seamless", "Unleash", "Next-Gen", "Revolutionize"
- NO AI copywriting cliches: "Delve", "Tapestry", "In the world of..."

## Component Bans

- NO hand-rolled SVG icons. Use Phosphor/HugeIcons/Radix/Tabler
- NO div-based fake screenshots (fake task lists, terminals, dashboards from styled divs)
- NO broken Unsplash links. Use `https://picsum.photos/seed/{seed}/{w}/{h}`
- NO shadcn/ui in default state — always customize radii, colors, shadows
- NO pill-shaped "New" and "Beta" badges — try square badges, flags, plain text

## Hero & Top-of-Page Bans

- NO version labels in hero: `V0.6`, `v2.0`, `BETA`, `INVITE-ONLY` (unless brief is a launch)
- NO "Brand · No. 01" style sub-eyebrows
- NO decoration text strips at hero bottom: `BRAND. MOTION. SPATIAL.`, `TYPE / FORM / MOTION`
- NO tiny tagline below CTAs in hero
- NO trust micro-strip inside hero ("Used by engineering teams at...")
- NO pricing teaser inside hero
- NO social-proof avatar row inside hero

## Section Numbering & Micro-Labels Bans

- NO section-number eyebrows: `00 / INDEX`, `001 · Capabilities`, `06 · how it works`
- NO `01 / 4` pagination on images or bento tiles
- NO `Scroll · 001 Capabilities` scroll cues with section-number prefix
- NO "Index of Work, 2018 - 2026" range labels as eyebrows

## Separator & Dot Bans

- Middle-dot (`·`) rationed: max 1 per line in metadata strips
- NO decorative colored status dots on every list/nav/badge (zero by default, only for real semantic state)

## Em-Dash Ban (Section 9.G — non-negotiable)

**Em-dash (`—`) is COMPLETELY banned.** Zero tolerance, no exceptions.

- Banned in headlines (use period or comma)
- Banned in eyebrows/labels/pills/button text/captions/nav items
- Banned in body copy (restructure: two sentences, comma, parentheses, or colon)
- Banned in quote attribution (use ` - ` with spaces)
- Banned in en-dash form (`–`) when used as separator (use hyphen for ranges)

ONLY permitted dash characters: regular hyphen `-` and minus sign in math.

## Marketing-Copy Bans

- NO "Quietly in use at" / "Quietly trusted by" headers
- NO "From the field" / "Field notes" / "On our desks" poetic labels
- NO weather/locale strips: "LIS 14:23 · 18°C"
- NO micro-meta-sentences under eyebrows
- NO generic step labels: "Stage 1 / Step 1 / Phase 01"
- NO version footers on marketing pages: `v1.4.2`, `Build 0048`
- NO "Reservation 412 of 800" live-stock counters as decoration

## Image & Label Bans

- NO pills/labels/tags overlaid on images
- NO photo-credit captions as decoration: "Field study no. 12 · Ines Caetano"
- NO scoring/progress bars with filled background tracks on landing pages

## Scroll & Motion Bans

- NO scroll cues: `Scroll`, `↓ scroll`, `Scroll to explore`
- NO `window.addEventListener('scroll')` in JS (use Motion useScroll, GSAP ScrollTrigger, IntersectionObserver, or CSS scroll-driven animations)
- NO custom scroll progress calculations using `window.scrollY` in React state
- NO `requestAnimationFrame` loops that touch React state
- NO GSAP/Motion mixed in the same component tree
- NO infinite loops on every card — only when section actively benefits from motion

## Banned Animation Patterns

- `window.addEventListener("scroll", ...)` — jank-prone, no batching
- Custom scroll progress using `window.scrollY` in React state
- `requestAnimationFrame` loops touching React state
- Static page that claims high MOTION_INTENSITY
- Half-built motion that breaks (cut-off ScrollTriggers, jumpy enters)
- Marquee more than once per page

## Hero Discipline (Hard Rules)

- Headline: max 2 lines on desktop
- Subtext: max 20 words AND max 3-4 lines
- Primary CTA: visible without scroll
- Top padding: max `pt-24` at desktop
- Stack: max 4 text elements (eyebrow OR brand strip, headline, subtext, CTAs)
- Font scale: `text-4xl md:text-5xl lg:text-6xl` default; `text-6xl md:text-7xl` only for 3-5 word headlines
- "Used by / Trusted by" logo wall goes UNDER hero, not inside it

## Navigation Rules

- Single line at desktop (condense labels, drop secondary, or hamburger if items don't fit)
- Height max 80px desktop (default 64-72px)
- No two-line nav at desktop — that is broken design

## Layout Discipline

- Section-Layout-Repetition: each layout family appears max once per page. 8 sections = at least 4 different families
- Zigzag Alternation Cap: max 2 consecutive image+text-split sections
- Bento Cell Count: N items = N cells. No empty cells
- Bento Background Diversity: at least 2-3 cells need real visual variation (image, gradient, pattern)
- Mobile collapse explicit per section for every multi-column layout

## Eyebrow Restraint

- Max 1 eyebrow per 3 sections (hero counts as 1)
- If section A has eyebrow, next 2 sections cannot
- Pre-flight check: count `uppercase tracking` instances. If > ceil(sectionCount/3), fail

## CTA Rules

- Button text fits one line at desktop (no wrapping)
- No duplicate CTA intent on one page ("Get in touch" + "Contact us" = same intent, pick one)
- Button contrast: WCAG AA min (4.5:1 body, 3:1 large text)
- Ghost buttons over photos need backdrop/scrim/stroke

## Quote Rules

- Max 3 lines of quote body
- Attribution: name + role + (optionally) company. Never name only
- Real typographic quotes or none. Not straight ASCII

## Code Quality Bans

- NO div soup — use semantic HTML: `<nav>`, `<main>`, `<article>`, `<section>`
- NO inline styles mixed with CSS classes
- NO hardcoded pixel widths — use relative units
- NO missing alt text on images
- NO arbitrary z-index values like `9999`
- NO commented-out dead code
- NO import hallucinations (check package.json first)

## Premium-Consumer Palette Ban

Banned hex families as default backgrounds/accents for premium-consumer briefs:

- Backgrounds: `#f5f1ea`, `#f7f5f1`, `#fbf8f1`, `#efeae0`, `#ece6db`, `#faf7f1`, `#e8dfcb`
- Accents: `#b08947`, `#b6553a`, `#9a2436`, `#9c6e2a`, `#bc7c3a`, `#7d5621`
- Text: `#1a1714`, `#1a1814`, `#1b1814`

**Default alternatives (rotate, do not reuse):**
- Cold Luxury: silver-grey + chrome + smoke
- Forest: deep green + bone + amber accent
- Black and Tan: true off-black + warm tan, sharp contrast
- Cobalt + Cream: saturated blue against single neutral
- Terracotta + Slate: warm rust against cool grey
- Olive + Brick + Paper: muted olive plus brick-red accent
- Pure monochrome + single saturated pop
