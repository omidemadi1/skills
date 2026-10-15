# Pre-Flight Check

Run every box before shipping. If any fails, the output is not done. This is NOT optional.

## Brief & Setup

- [ ] Brief inference declared (one-line design read from Section 0.B)
- [ ] Dial values explicit and reasoned from the brief
- [ ] Design system chosen from design-systems.md or aesthetic labeled honestly
- [ ] Redesign mode detected and audit performed (if applicable)

## The Three Locks

- [ ] **ZERO em-dashes** (`—`) anywhere on page. Headlines, eyebrows, pills, body, quotes, attribution, captions, buttons, alt text. Zero.
- [ ] **Page Theme Lock:** ONE theme (light/dark/auto) for whole page. No section flips
- [ ] **Color Consistency Lock:** one accent color used identically across all sections
- [ ] **Shape Consistency Lock:** one corner-radius system applied consistently

## Accessibility

- [ ] Button contrast: every CTA text readable against background (WCAG AA 4.5:1)
- [ ] CTA button wraps to one line at desktop
- [ ] Form contrast: inputs, placeholders, focus rings, labels all pass WCAG AA
- [ ] Reduced motion wrapped for everything MOTION_INTENSITY > 3
- [ ] Skip-to-content link present for keyboard users
- [ ] All images have meaningful alt text

## Typography

- [ ] Serif discipline: if serif used, NOT Fraunces or Instrument_Serif (or justified)
- [ ] Italic descender clearance: every italic word with y/g/j/p/q has `leading-[1.1]` min + `pb-1`
- [ ] Inter not used as default (unless brief explicitly asks for it)

## Color

- [ ] Premium-consumer palette check: if brief is premium-consumer, palette is NOT beige+brass+oxblood+espresso default
- [ ] No AI-purple/mesh blob gradients as default
- [ ] Max 1 accent, saturation < 80%

## Hero

- [ ] Hero fits viewport: headline ≤ 2 lines, subtext ≤ 20 words AND ≤ 4 lines
- [ ] CTA visible without scroll
- [ ] Hero font scale planned around image size
- [ ] Hero top padding: max `pt-24` at desktop
- [ ] Hero stack discipline: max 4 text elements (eyebrow OR brand strip, headline, subtext, CTAs)
- [ ] No tiny tagline below CTAs, no trust micro-strip in hero
- [ ] Logo wall lives UNDER hero, not inside it

## Layout

- [ ] Eyebrow count: ≤ ceil(sectionCount / 3). Hero counts as 1
- [ ] Split-header ban: no "left headline + right small explainer" as section header
- [ ] Zigzag alternation cap: no 3+ consecutive image+text-split sections
- [ ] Section-layout-repetition: no two sections share same layout family (4+ families across 8 sections)
- [ ] Navigation on ONE line at desktop, height ≤ 80px
- [ ] Bento has rhythm AND exact cell count (N items = N cells)
- [ ] Bento background diversity: at least 2-3 cells with real visual variation
- [ ] Mobile collapse explicit per section

## CTAs & Buttons

- [ ] No duplicate CTA intent on page ("Get in touch" + "Let's talk" = same intent)
- [ ] Button text fits one line at desktop
- [ ] Ghost buttons over photos have backdrop/scrim/stroke

## Content

- [ ] Copy self-audit: every visible string re-read, no grammatically broken or AI-hallucinated phrases
- [ ] No fake-precise numbers without justification
- [ ] One copy register per page
- [ ] Quotes ≤ 3 lines, attribution clean
- [ ] Long lists use right UI component (not default `<ul>` with `divide-y` for >5 items)

## Anti-Slop Bans

- [ ] No pills/labels overlaid on images
- [ ] No photo-credit captions as decoration
- [ ] No version footers on marketing pages
- [ ] No micro-meta-sentences under eyebrows
- [ ] No decoration text strips at hero bottom
- [ ] No floating top-right sub-text in section headings
- [ ] No scoring/progress bars with filled background tracks
- [ ] No locale/city/time/weather strips (unless brief is genuinely place-focused)
- [ ] No scroll cues (`Scroll`, `↓ scroll`)
- [ ] No version labels in hero (V0.6, BETA) unless brief is a launch
- [ ] No section-numbering eyebrows (`00/INDEX`, `001·Capabilities`)
- [ ] No decorative dots (zero by default)
- [ ] No `border-t` + `border-b` on every row of long lists

## Images & Visuals

- [ ] Real images used (gen-tool → picsum-seed → placeholder slots)
- [ ] NO div-based fake screenshots
- [ ] NO hand-rolled decorative SVGs
- [ ] Logo wall uses real SVG logos (Simple Icons / devicon), not plain text wordmarks
- [ ] Logo wall = logos only (no category labels underneath)

## Motion

- [ ] Every animation justified in one sentence
- [ ] Marquee max one per page
- [ ] No `window.addEventListener('scroll')` — using Motion/GSAP/IntersectionObserver
- [ ] GSAP sticky-stack/horizontal-pan per canonical skeletons
- [ ] Motion isolated in client-leaf components with `'use client'`

## Technical

- [ ] Viewport stability: `min-h-[100dvh]`, never `h-screen`
- [ ] `useEffect` animations have strict cleanup functions
- [ ] Empty/loading/error states provided
- [ ] Cards omitted in favor of spacing where possible
- [ ] Icons from allowed libraries only (Phosphor/HugeIcons/Radix/Tabler)
- [ ] No AI Tells: Inter default, AI-purple, three-equal cards, Jane Doe, Acme, "Quietly in use at"
- [ ] Core Web Vitals plausible (LCP < 2.5s, INP < 200ms, CLS < 0.1)
- [ ] One design system per project (no Material + shadcn mixed)
- [ ] Dark mode tested in both modes
