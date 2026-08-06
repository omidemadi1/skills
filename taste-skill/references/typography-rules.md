# Typography Rules

## Defaults

- **Display/Headlines:** `text-4xl md:text-6xl tracking-tighter leading-none`
- **Body/Paragraphs:** `text-base text-gray-600 leading-relaxed max-w-[65ch]`

## Sans Font Choice

**Default (pick first):** Geist, Outfit, Cabinet Grotesk, Satoshi

**Discouraged as default:** Inter

**Override:** Inter is acceptable when user explicitly asks for neutral/Linear-style, or brief is public-sector/accessibility-first.

**Pairings to know:**
- Geist + Geist Mono
- Satoshi + JetBrains Mono
- Cabinet Grotesk + Inter Tight
- GT America + IBM Plex Mono

## Serif Discipline

Serif is **very discouraged as default** for any project. "It feels creative/premium/editorial" is NOT a reason to reach for serif.

**Serif is only acceptable when ONE of these is true:**
1. Brand brief literally names a serif font, OR
2. Aesthetic is genuinely editorial/luxury/publication/manuscript/heritage/vintage AND you can articulate why this specific serif fits this specific brand

**For everything else** (creative agency, design studio, modern brand, premium consumer, portfolio, lifestyle): default sans-serif display (Geist Display, ABC Diatype, Söhne Breit, Cabinet Grotesk Display, Inter Display, PP Neue Montreal).

**Specifically banned as defaults:** Fraunces and Instrument_Serif (the two LLM-favorite display serifs).

**If serif is justified**, rotate from this pool (do NOT reuse across consecutive projects):
PP Editorial New, GT Sectra Display, Cardinal Grotesque, Reckless Neue, Tiempos Headline, Recoleta, Cormorant Garamond, Playfair Display, EB Garamond, IvyPresto, Migra, Editorial Old, Saol Display, Domaine Display, Canela, Schnyder, Tobias, NB Architekt, ITC Galliard

## Emphasis in Headlines

When emphasizing a word within a headline, use **italic or bold of the SAME font**. Do NOT inject a random serif word into a sans headline (or vice versa). Mixed-family emphasis is amateur. Italic/bold emphasis in the same family is the right move.

## Italic Descender Clearance (mandatory)

When italic is used in display type and the word contains a descender letter (`y g j p q`), `leading-[1]` or `leading-none` will clip the descender.

- Use `leading-[1.1]` minimum
- Add `pb-1` or `mb-1` reserve on the wrapping element
- Audit every italic word in display headlines before shipping

## Numbers in Data-Heavy UIs

Use a monospace font or enable tabular figures (`font-variant-numeric: tabular-nums`) for data-heavy interfaces.

## Letter-Spacing

- Negative tracking for large headers
- Positive tracking for small caps or labels
- Never use all-caps subheaders everywhere — try lowercase italics, sentence case, or small-caps

## Orphaned Words

Single words sitting alone on the last line. Fix with `text-wrap: balance` or `text-wrap: pretty`.

## Weight Hierarchy

Don't rely only on Regular (400) and Bold (700). Introduce Medium (500) and SemiBold (600) for more subtle hierarchy.
