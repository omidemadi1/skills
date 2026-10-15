---
name: brand-assets-gen
description: Generate a comprehensive brand-assets file from spec documents (design.md and requirements.md). The skill guides the model through a structured psychological reasoning process: deeply understanding the product, analyzing the target audience's psychology, then deriving every brand decision (colors, fonts, logo, voice, etc.) from evidence-based reasoning about what will attract and influence that specific audience. Outputs are unique to each project because the brand identity flows from the project's unique characteristics and user base.
---

# Brand Assets Generator

This skill generates a brand-assets file by guiding the model through a **structured psychological reasoning process**. Every brand decision is derived from understanding the product and its users — not from fixed tables or pre-built frameworks. Two different projects will naturally produce completely different brand identities because the audiences, purposes, and emotional promises are different.

**Core principle**: The skill teaches *how to think* about brand identity. It asks specific questions at each stage and requires evidence-based reasoning. The model's output quality depends on how deeply it engages with each question.

---

## Stage 1: Deep Product Understanding

Read `design.md` and `requirements.md` thoroughly. Then answer these questions — write the answers down, they feed into every subsequent stage:

1. **What does this product do?** — Summarize in one sentence. Not what it is technically, but what it does for the human using it.

2. **What is the core problem it solves?** — What frustration, inefficiency, or pain does the user face without this product?

3. **What is its unique approach?** — How does it solve this problem differently from alternatives? What would competitors do differently?

4. **What is the product's emotional promise?** — When the user successfully uses this product, what feeling do they walk away with? (Not a feature — a feeling. E.g., "confidence that I look put-together" or "relief that I don't have to remember everything.")

5. **What design principles guide it?** — Extract from the design.md principles. These directly constrain the brand identity. E.g., if the product says "latency over complexity," the brand must feel clean and efficient, not ornate.

6. **What existing aesthetic references exist?** — Are there style mentions in the specs? (e.g., "Pinterest-like," "warm off-white background #FAF8F5," "minimalist," specific UI patterns). These are non-negotiable anchors for the brand.

7. **What is the product's domain?** — Fashion, productivity, finance, health, social, etc. This determines the visual language universe.

---

## Stage 2: Target Audience Psychology

This is the most important stage. Everything downstream depends on how well you understand the user. Answer every question:

1. **Who is the primary user?** — Age range, gender lean (if any), lifestyle, profession, interests. Use evidence from the spec files (requirements often describe target users). If the specs don't specify, infer from the product's purpose — who would benefit most?

2. **What is their daily life like?** — Are they busy professionals? Creative hobbyists? Health-conscious parents? This determines whether the brand should feel efficient, inspiring, nurturing, etc.

3. **What pain points drive them to this product?** — Not what the product does, but what emotional state they're in before using it. E.g., "frustrated that they own 100 clothes but feel like they have nothing to wear" or "overwhelmed by meeting follow-ups falling through cracks."

4. **What does success look like for them?** — What does the user aspire to? What's the "after" state? E.g., "walking out the door feeling confident" or "knowing every action item is tracked."

5. **What do they fear or want to avoid?** — Privacy concerns? Looking foolish? Wasting money? Being overwhelmed by complexity? This shapes whether the brand should feel safe, discreet, simple, etc.

6. **How do they feel when they open the app?** — In what emotional state do they arrive? Frustrated? Curious? In a hurry? Relaxed? The brand should meet them where they are and guide them to where they want to be.

7. **What other products/apps do they likely use?** — What are their visual reference points? A user who uses Notion has different expectations than one who uses Instagram. This calibrates the expected visual sophistication.

8. **What visual elements attract this audience?** — Based on their demographics, interests, and lifestyle: do they respond to warm colors or cool? Bold or subtle? Playful or sophisticated? Minimal or rich? Use color psychology principles here:
   - Warm tones (rose, coral, amber) → approachable, personal, nurturing
   - Cool tones (blue, teal, violet) → trust, intelligence, calm
   - Earth tones (sage, terracotta, cream) → organic, grounded, authentic
   - Deep/rich tones (navy, burgundy, forest) → premium, authoritative, established
   - Bright/saturated tones (electric blue, hot pink) → energetic, youthful, disruptive
   - Muted/dusty tones (dusty rose, slate, taupe) → refined, understated, elegant

---

## Stage 3: Brand Personality Definition

Based on Stages 1 and 2, define the brand as if it were a person:

1. **Personification** — If this product were a person, who would they be? Describe them in 2-3 sentences. E.g., "A knowledgeable friend who happens to be a great stylist — they never push you to buy anything, they just help you discover what you already have." or "A sharp executive assistant who anticipates what you need before you ask."

2. **Three defining adjectives** — Choose exactly 3 adjectives that capture the brand personality. E.g., "warm, knowledgeable, confident" or "efficient, crisp, reliable." These adjectives must emerge from the product purpose + audience psychology, not be picked randomly.

3. **Brand archetype** — From standard archetypes (Sage, Caregiver, Creator, Magician, Explorer, Ruler, Rebel, Hero, Lover, Jester, Everyman, Innocent), choose the ONE that best fits. Justify with specific evidence from Stages 1 and 2. E.g., "The Sage because the product's core value is intelligent recommendation based on data analysis, and the target audience values expertise and trust."

4. **What the brand is NOT** — Name 1-2 archetypes that definitely don't fit, and explain why. This constrains the personality space and prevents generic answers. E.g., "Not The Jester — the product handles personal data and makes decisions that affect daily confidence; humor would undermine trust."

5. **Emotional core** — In one sentence, what feeling should the brand evoke at first encounter? E.g., "The relief of realizing your wardrobe has more to offer than you thought" or "The calm confidence of knowing nothing is falling through the cracks."

---

## Stage 4: Color Palette Construction

Derive colors from the audience psychology and brand personality. Do NOT copy colors from other brands or use generic "tech blue" defaults.

**For each color, you must answer**: Why this specific hue, saturation, and lightness for THIS audience and THIS product?

1. **Primary color** — This is the brand's signature. Choose based on:
   - What color family communicates the product's core function to this audience?
   - What color evokes the emotional core you defined in Stage 3?
   - What color differentiates from competitors in this space?
   - State the exact hex code, name the color, and write a 1-sentence psychological rationale.

2. **Secondary color** — Complements the primary. Choose based on:
   - What color creates harmony with the primary?
   - What role does it play? (Supporting elements, hover states, secondary actions)
   - State the exact hex, name, and rationale.

3. **Accent color** — Used sparingly for CTAs, highlights, alerts. Choose based on:
   - What color creates enough contrast to draw attention?
   - What color signals action/urgency without clashing with the primary?
   - State the exact hex, name, and rationale.

4. **Background surface color** — The canvas everything sits on. Consider:
   - Does the spec file mention a specific background? (e.g., #FAF8F5) → Use it.
   - Does the product feel warm and inviting (off-white, cream) or clean and clinical (white, light gray)?
   - State the exact hex.

5. **Text color** — Primary text for readability. Consider:
   - Avoid pure black (#000000) — it creates harsh contrast. Use a near-black that feels intentional.
   - State the exact hex and name.

6. **Write a color rationale paragraph** — In 3-4 sentences, explain how the complete palette serves the target audience. Connect each color to the audience psychology from Stage 2 and the brand personality from Stage 3.

---

## Stage 5: Typography Selection

Typography carries personality. Choose fonts that match the brand character you defined.

1. **Typography personality** — Based on Stage 3 adjectives:
   - Should the type feel **modern/tech** (geometric sans) or **classic/premium** (serif)?
   - Should it feel **warm/friendly** (rounded, soft terminals) or **precise/authoritative** (sharp, clean)?
   - Should it feel **artistic/expressive** (display, high contrast) or **functional/reliable** (neutral, workhorse)?
   - Justify with reference to the audience and brand personality.

2. **Heading font** — Choose a specific font family. Consider:
   - Does it match the typography personality above?
   - Is it available as a web font? (Google Fonts, Adobe Fonts, or system font)
   - Does it pair well with the body font?
   - State the font name, source, and why it fits.

3. **Body font** — Choose for readability. Consider:
   - Must be highly readable at 14-16px for extended reading.
   - Should complement, not compete with, the heading font.
   - Inter is a safe default for UI body text — but justify if you choose something else.

4. **Type scale** — Define the sizing hierarchy. Standard scale for web apps:

   | Level | Size | Weight | Line Height |
   |-------|:----:|:------:|:-----------:|
   | H1 | 48px | Bold (700) | 1.2 |
   | H2 | 36px | SemiBold (600) | 1.25 |
   | H3 | 28px | SemiBold (600) | 1.3 |
   | H4 | 22px | Medium (500) | 1.35 |
   | Body | 16px | Regular (400) | 1.6 |
   | Small | 14px | Regular (400) | 1.5 |
   | Caption | 12px | Medium (500) | 1.4 |

---

## Stage 6: Logo and Visual Symbol

The logo must encode the product's core value in visual form.

1. **Defining capability** — From Stage 1: What is the product's single most defining capability that the logo should visually reference?

2. **Visual metaphor** — What visual symbol represents this capability and resonates with the audience? Consider:
   - What objects, shapes, or concepts are associated with the product's domain?
   - What visual metaphor captures the emotional promise (Stage 1)?
   - What symbol would the target audience (Stage 2) immediately understand?
   - E.g., a wardrobe app might reference hangers, fabric, mirrors, or organization. A meeting notes app might reference speech bubbles, flowing lines, or connected nodes.
   - Describe the icon concept in detail, explaining the psychological connection.

3. **Logo type** — Choose one:
   - **Combination mark** (icon + wordmark) — best when the brand is new and needs both recognition and name awareness
   - **Wordmark only** — best when the name itself is distinctive and memorable
   - **Symbol only** — best when the brand is already well-known
   - **Emblem** — best for heritage/traditional brands
   - Justify your choice based on the product's stage and audience.

4. **Wordmark styling** — How should the product name be set? Consider case (lowercase feels friendly, titlecase feels professional), weight, and spacing.

5. **Logo usage rules** — Define: minimum size, clear space, acceptable backgrounds, prohibited uses.

---

## Stage 7: Brand Voice and Tone

How the brand speaks is as important as how it looks.

1. **Voice personality** — Write 2-3 sentences describing how the brand would talk if it were a person. Ground this in the brand personality (Stage 3) and audience (Stage 2). E.g., "The brand speaks like a knowledgeable friend who happens to be a great stylist — confident but never condescending, specific but never overwhelming."

2. **Formality calibration** — On a scale of 1-10 (1 = very casual, 10 = very formal), where does this brand sit? Justify:
   - What audience expectations drive this? (Gen Z expects casual; enterprise expects formal)
   - What product domain demands this? (medical = more formal; lifestyle = more casual)

3. **In-brand words** — List 6-8 words/phrases that feel natural for this brand. These should emerge from the brand personality and product domain. E.g., for a wardrobe app: "discover, combine, style, wardrobe, pair, outfit." For a meeting notes app: "capture, track, follow-up, action, sync, clarify."

4. **Out-of-brand words** — List 5-6 words that feel wrong for this brand and explain why. These should be words that clash with the personality you defined. E.g., a wardrobe app that positions itself as "your existing wardrobe, styled" should avoid: "purchase, shop, buy, new collection, trend."

5. **Error message tone** — How should the brand handle failures? Direct and solution-focused? Warm and reassuring? Technical and precise? Write an example error message that sounds like this brand.

6. **Success message tone** — How should the brand celebrate achievements? Enthusiastic? Calm and specific? Write an example success message.

---

## Stage 8: Audio Identity

Audio reinforces personality. Design sounds that match the brand character.

1. **Sound character** — Based on the brand personality, should the audio identity be:
   - Soft and satisfying (calming products)?
   - Crisp and confident (efficiency-focused products)?
   - Warm and organic (lifestyle/personal products)?
   - Minimal and functional (products where audio is secondary)?
   Justify based on the design principles and audience expectations.

2. **Sound cues** — Define specific sounds for:
   - Success action completed
   - Warning/caution
   - Error/failure
   - Processing started/completed
   For each, describe: instrument/texture, duration, pitch direction, and why it matches the brand.

3. **Brand audio signature** — A short (2-3 second) signature sound for brand moments. Describe the musical character, key (if applicable), tempo, and instrumentation.

4. **Volume philosophy** — How prominent should audio be in the experience? (Background whisper vs. intentional punctuation)

---

## Stage 9: Graphic Templates

Define reusable visual templates that carry the brand identity into communications.

1. **Product patterns to carry forward** — What layout/visual patterns from the product itself (from design.md) should appear in brand materials? E.g., if the product uses card-based layouts with rounded corners and warm backgrounds, brand templates should echo this.

2. **Template definitions** — For each template below, define: dimensions, background color, layout structure, typography usage, logo placement, and spacing. Templates needed:
   - **Social media post** (Instagram square: 1080×1080)
   - **Email header** (600×300)
   - **Presentation slide** (1920×1080, 16:9)
   - **App screenshot frame** (device-appropriate dimensions)

3. **Shared visual rules** — Define: corner radius, shadow style, border treatment, grid unit, margin/padding values, and the "never" rules (things that must never appear in brand materials).

---

## Stage 10: Coherence Review

Before writing the final output, review all decisions for internal consistency:

1. **Story check** — Read through all your decisions. Do they tell one consistent story? If someone saw only the colors, would they expect the voice you chose? If they read only the slogan, would it match the logo concept?

2. **Audience check** — For every major decision, ask: "Would the target audience from Stage 2 find this appealing?" If the audience is fashion-conscious young women and the palette feels corporate blue, something is wrong.

3. **Domain check** — Does the brand identity feel appropriate for this product's domain? A medical app shouldn't feel playful; a lifestyle app shouldn't feel clinical.

4. **Differentiation check** — Does this brand identity look different from what competitors in this space typically do? If every competitor uses blue, this brand should probably use something else.

5. **Contradiction check** — Are there any decisions that contradict each other? E.g., choosing "friendly, warm" as personality traits but then picking cold steel-gray as the primary color.

---

## Output Structure

Write the final brand-assets file using this structure. Fill in your Stage 1-9 analysis and decisions. The section headings below are fixed — use them exactly. Within each section, your reasoning and decisions should be substantive and specific to this project.

```
# Brand Assets: [Product Name]

## 1. Logo and Trademark

**Brand Name**: [Product name]

**Logo Type**: [Your choice from Stage 6 — with brief justification]

**Icon Concept**: [Your visual metaphor from Stage 6 — describe the symbol and its psychological meaning]

**Wordmark**: [Your wordmark styling from Stage 6]

**Logo Variations**:
- Primary: [description]
- Secondary: [description]
- Monochrome: [description]

**Minimum Size**: [pixels]

**Clear Space**: [rule]

**Never**: [prohibited uses]

## 2. Color Palette

[Your color rationale paragraph from Stage 4]

| Role | Name | Hex | Psychological Rationale |
|------|------|:---:|------------------------|
| Primary | [name] | #[hex] | [1-sentence reason] |
| Secondary | [name] | #[hex] | [1-sentence reason] |
| Accent | [name] | #[hex] | [1-sentence reason] |
| Background | [name] | #[hex] | [1-sentence reason] |
| Text | [name] | #[hex] | [1-sentence reason] |

## 3. Typography and Fonts

**Typography Personality**: [your 1-2 sentence description from Stage 5]

**Heading Font**: [font name] — [1-sentence justification]

**Body Font**: [font name] — [1-sentence justification]

| Level | Size | Weight | Line Height | Font |
|-------|:----:|:------:|:-----------:|:-----|
| H1 | 48px | Bold (700) | 1.2 | [heading font] |
| H2 | 36px | SemiBold (600) | 1.25 | [heading font] |
| H3 | 28px | SemiBold (600) | 1.3 | [heading font] |
| H4 | 22px | Medium (500) | 1.35 | [heading font] |
| Body | 16px | Regular (400) | 1.6 | [body font] |
| Small | 14px | Regular (400) | 1.5 | [body font] |
| Caption | 12px | Medium (500) | 1.4 | [body font] |

## 4. Visual Identity Guide

**Logo Usage**: [describe lockup]

**Color Hierarchy**: [how each color is used]

**Typography Rules**: [font usage guidelines]

**Imagery Style**: [photography/illustration direction — derived from product domain and audience]

**Spacing**: [grid system, gutters, padding]

**Always/Never Rules**: [brand do's and don'ts]

**Grid & Containers**: [layout patterns, corner radius, shadows]

## 5. Brand Slogan

**Slogan**: "[Your slogan from the analysis]"

**Rationale**: [1-2 sentences on why this slogan connects with the target audience]

## 6. Tone of Voice

**Voice Personality**: [your description from Stage 7]

**Formality Level**: [your 1-10 rating with justification]

**In-Brand Words**: [your word list]

**Out-of-Brand Words**: [your word list with reasons]

**Error Message Example**: "[your example]"

**Success Message Example**: "[your example]"

## 7. Audio Identity

**Sound Character**: [your description from Stage 8]

| Cue | Sound | Duration | Description |
|-----|-------|:--------:|-------------|
| Success | [instrument/pitch] | [seconds] | [description] |
| Warning | [instrument/pitch] | [seconds] | [description] |
| Error | [instrument/pitch] | [seconds] | [description] |
| Processing | [instrument/pitch] | [seconds] | [description] |

**Brand Audio Signature**: [your 2-3 second signature description]

**Volume Philosophy**: [your approach]

## 8. Graphic Templates

### Template 1: Social Media Post
[dimensions, background, layout, logo placement]

### Template 2: Email Header
[dimensions, background, layout, logo placement]

### Template 3: Presentation Slide
[dimensions, background, layout, logo placement]

### Template 4: App Screenshot Frame
[dimensions, background, layout, logo placement]

**Shared Rules**:
- [corner radius, shadow, border, grid, spacing]
- [never rules]
```

---

## Writing Guidelines

- **Be specific** — Not "a warm color" but "Terracotta (#C07A5B) — earthy warmth that signals authenticity to fashion-conscious users who value organic, lived-in aesthetics over artificial perfection."
- **Cite the spec files** — When a decision comes from the design.md or requirements.md, reference it. E.g., "The design principle 'latency over complexity' calls for clean, efficient typography — hence choosing Inter over a decorative display font."
- **Connect psychology to decisions** — Every color, font, and tone choice should trace back to either the audience psychology (Stage 2) or the brand personality (Stage 3).
- **Write the rationale, not just the answer** — The 1-sentence rationale in each table row is what makes this skill work. It's what makes the decision traceable and reviewable.
- **Never use generic defaults** — If you catch yourself writing "tech blue (#3B82F6)" or "startup purple (#7C3AED)" without specific justification for THIS audience, stop and reconsider.
