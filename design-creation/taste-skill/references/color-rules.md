# Color Rules

## Core Rules

- Max 1 accent color per page. Saturation < 80% by default
- One palette per project. Do not fluctuate between warm and cool grays
- Pure `#000000` background → replace with off-black, dark charcoal, or tinted dark
- Generic `box-shadow` → tint shadows to match background hue
- Flat design with zero texture → add subtle noise, grain, or micro-patterns
- Perfectly even gradients → break with radial gradients, noise overlays, or mesh gradients

## The LILA RULE

The "AI Purple / Blue glow" aesthetic is discouraged as default. No automatic purple button glows, no random neon gradients.

**Default:** Use neutral bases (Zinc / Slate / Stone) with high-contrast singular accents (Emerald, Electric Blue, Deep Rose, Burnt Orange).

**Override:** If brand or brief explicitly asks for purple/violet/lila, embrace it — but execute with intent: consistent palette, harmonised neutrals, restrained gradients. Not generic AI gradient slop.

## Color Consistency Lock (mandatory)

Once an accent color is chosen for a page, it is used on the WHOLE page. A warm-grey site does not suddenly get a blue CTA in section 7. A rose-accented site does not get a teal status badge in the footer. Pick one accent, lock it, audit every component before shipping.

## Premium-Consumer Palette Ban (mandatory)

For premium-consumer briefs (cookware, wellness, artisan, luxury, heritage craft, DTC home goods), the LLM default is warm beige/cream + brass/clay/oxblood/ochre + espresso/ink dark text.

**Banned hex families:**

Backgrounds: `#f5f1ea`, `#f7f5f1`, `#fbf8f1`, `#efeae0`, `#ece6db`, `#faf7f1`, `#e8dfcb`
Accents: `#b08947`, `#b6553a`, `#9a2436`, `#9c6e2a`, `#bc7c3a`, `#7d5621`
Text: `#1a1714`, `#1a1814`, `#1b1814`

**Default alternatives (rotate, do NOT reuse):**

| Palette | Colors | Inspiration |
|---|---|---|
| Cold Luxury | silver-grey + chrome + smoke | Tesla, Apple Watch Hermes |
| Forest | deep green + bone + amber accent | Filson, Patagonia premium |
| Black and Tan | true off-black + warm tan, sharp contrast | No beige |
| Cobalt + Cream | saturated blue against single neutral | No brass |
| Terracotta + Slate | warm rust against cool grey | No brass |
| Olive + Brick + Paper | muted olive + brick-red accent | — |
| Mono + pop | off-white + off-black + one bright accent | Electric blue, emerald, hot pink |

**Palette-rotation rule:** If previous premium-consumer project used beige+brass, this one MUST use a different family.

**Override:** Beige+brass+espresso acceptable ONLY when brand brief explicitly names those colors, or brand is genuinely vintage/artisan/warm-craft AND you can articulate why.

## Dark Mode Color Rules

- Off-black (zinc-950, near-black warm gray) and off-white. Pure values kill depth
- WCAG AA minimum for body text, AAA target for hero copy
- Visual hierarchy that works in light must work in dark
- Primary brand color stays recognisable in dark mode. Don't desaturate
- Respect `prefers-color-scheme: dark` unless brand insists on one mode

## Shadows

- Tint shadows to background hue. No pure-black drop shadows on light backgrounds
- For `VISUAL_DENSITY > 7`: generic card containers are banned. Data metrics breathe in plain layout
