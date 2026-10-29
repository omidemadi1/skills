# Component Playbooks — selection ladders and why choices fail

> Read this at Stage 4 (BOM and alternatives). Each section gives a **primary → fallback →
> avoid** ladder with the trigger that tells you to switch. Use the ladder instead of
> rediscovering the same trade-off on every project.

## Contents

1. Power path
2. LED strip
3. Joining LED strip segments
4. Switching and control
5. Diffusion and optics
6. Adhesives and fastening
7. Cutting and printing
8. Enclosure and structure
9. Substitution ladder (one-page summary)
10. Why choices fail — recurring patterns

---

## 1. Power path

**Primary:** a supply that matches the load voltage directly.
**Fallback:** a certified adapter with a DC jack.
**Avoid:** boosting 5V to 12V for anything more than a small load; 220V inside a handmade box.

| Option | Best for | Practical limit | Pros | Cons |
|---|---|---|---|---|
| **USB-C PD trigger, fixed 12V** | Sellable product, one-cable design | ~1–2A at 12V depending on charger | No boost losses; clean; small | Needs a PD-capable charger; trigger module adds a part |
| **12V wall adapter + DC jack** | Prototype, bench test, budget build | 1–3A | Cheap, reliable, easy to source | External brick; jack takes space |
| **5V USB direct** | 5V strip, small load | ~2A with a good charger | Simplest; no converter | Voltage drop over long cable; dimmer |
| **Boost 5V→12V (MT3608 class)** | Tiny load only | ~0.3–0.5A at 12V in practice | Cheap; one module | Hot near limit; efficiency loss; input current is high |
| **220V strip / mains driver** | Never inside a handmade enclosure | — | — | Shock/fire risk; certification; not worth it |

**Switch trigger:** if the measured load exceeds ~50% of the converter's rated output, or the
module case exceeds 60°C, change the power path — do not add a fan or a heatsink to a part that
was never sized for the job.

**Checks before buying:** input voltage range, output current at the actual input voltage,
switch-current limit, efficiency curve, quiescent current, connector type, and whether the
USB-C socket has 5.1kΩ CC pulldowns.

---

## 2. LED strip

| Type | Typical power | Look | Best for |
|---|---|---|---|
| **5050 12V, 60 LED/m** | ~14.4W/m (1.2A/m) | Visible dots unless diffused | General backlight, cheap |
| **2835 12V** | ~7–10W/m | Smaller dots, efficient | Slim boxes, lower heat |
| **COB 12V** | ~8–15W/m | Continuous line, no dots | Premium even light, short standoff |
| **5V USB strip** | ~4–8W/m | Dots; voltage drop | Small, simple, no driver |

Rules:

- Specify **CCT** (2700/3000/4000/6000–6500K) and **CRI** (≥90 for photos/art) separately from
  "white".
- Cut only on the marked lines; the copper pads are not continuous.
- Keep 12V runs short or use a bus; voltage drop shows as a dim far end.
- In a closed box, derate 20–30% or provide a path for heat.
- The 3M backing is not a permanent structural fixing on its own — add mechanical retention or
  silicone at the ends.

**Switch trigger:** if the diffuser cannot be placed ≥15mm away, prefer COB over 5050.

---

## 3. Joining LED strip segments

**Primary:** solderless connector of the correct width (8/10mm) for serviceable joints.
**Fallback:** direct solder with a temperature-controlled iron for permanent joints.
**Avoid:** pin headers, twisted strands, or an unregulated high-watt iron.

| Method | Pros | Cons | Use when |
|---|---|---|---|
| Solderless connector | No heat; replaceable; fast | Bulkier; contact quality varies | Product, serviceable build |
| Solder + heat-shrink | Compact; reliable if done well | Needs skill and temperature control | Permanent harness, middle cuts |
| Pin header | Cheap | Does not grip the pad; strands slip | Never on a load-bearing joint |

**Solder recipe:** 350°C max, 2–3 seconds per joint, pre-tin pad and wire, flux, 0.5–0.8mm
solder, heat-shrink, then strain-relieve. If the pad lifts or the plastic softens, the iron is
too hot or the contact is too long — stop and change the tool, not the technique.

**Test:** pull test (~1kg, 10s) plus continuity (<1Ω).

---

## 4. Switching and control

**Primary:** a ready-made module rated for the load (12V touch dimmer, relay module).
**Fallback:** logic output + logic-level MOSFET + gate resistor + pulldown.
**Avoid:** driving a load directly from a logic output.

| Option | Pros | Cons | Use when |
|---|---|---|---|
| Ready 12V touch dimmer | Handles load and dimming; few parts | Fixed form factor; slightly pricier | Product, fast build |
| TTP223 + AO3400 MOSFET | Cheap; flexible | Needs gate resistor, pulldown, layout | Custom UI, breadboard |
| TTP223 alone | Tiny | Sources only a few mA; cannot switch a strip | Never for a load |

Notes:

- TTP223 has a **toggle/momentary jumper**; decide which behaviour you want before wiring.
- Add 100nF at VCC and 100–470µF near the strip.
- A MOSFET needs a **logic-level** gate threshold; a random IRF part may not fully turn on at
  3.3V.

---

## 5. Diffusion and optics

**Primary:** one 3mm opal/diffuser acrylic sheet at 15–25mm from the strip.
**Fallback:** tracing paper for a prototype.
**Avoid:** milky acrylic alone (when colour/evenness matters), or stacking milky + diffuser.

| Option | Pros | Cons | Use when |
|---|---|---|---|
| Opal diffuser 3mm | Even light; good transmission | Needs standoff; cost | Final piece |
| Tracing paper | Very cheap; easy to test | Fragile; yellowing; not cleanable | Prototype only |
| Milky acrylic alone | Cheap; structural | Hotspots; colour shift; loses light | Low-expectation build |

**Why "milky acrylic made my light yellow" is usually wrong:** the diffuser does not change
colour temperature. Yellow output comes from a warm-white strip (3000K), an aged/yellowed
sheet, or a coloured backing. Check CCT before blaming the diffuser.

**Switch trigger:** visible hotspots at 30cm → increase standoff or switch to COB; colour is
wrong → change the strip's CCT/CRI, not the diffuser.

---

## 6. Adhesives and fastening

| Adhesive | Service temp | Strength | Best for | Avoid for |
|---|---|---|---|---|
| Glue stick | ~50°C | Low | Paper, temporary positioning | Anything under load or heat |
| Hot glue | ~60–80°C | Medium | Prototype, cable tacking | LED strips, warm enclosures |
| 3M double-sided tape | ~90°C+ | Medium-high | LED strip, panels | Dirty/porous surfaces |
| Neutral silicone | ~200°C | Medium | Permanent LED fixing, glass | Fast production (cure time) |
| Epoxy | ~120°C+ | High | Structural joints | Repairable assemblies |
| CA (superglue) | ~80°C | High but brittle | Small non-flexing joints | Impacts, thermal cycling |

Rules: clean and degrease the surface; apply pressure for the tape's rated time; respect cure
time; never use a paper adhesive on a thermal or load-bearing part.

---

## 7. Cutting and printing

**Primary for repeatable shapes:** plotter/vinyl cutter with registration marks, or laser/CNC.
**Fallback for one-offs:** fresh scalpel blade + steel ruler + cutting mat.
**Avoid:** a used utility-knife blade on glossy photo paper.

- Cut glossy prints **from the back** to avoid surface chipping.
- Change the blade per print; a dull blade tears fibres and leaves a white edge.
- A pencil-style knife gives better control on curves than a snap-off utility knife.
- Laser cutting leaves a burnt edge and smell; not ideal for a visible print.
- For MDF: 3mm is a prototype; 6mm or plywood for a permanent frame.

**Switch trigger:** more than 2 identical pieces, or visible edge tear → move to a plotter.

---

## 8. Enclosure and structure

**Primary:** 6mm MDF/plywood frame or laser-cut panels with a serviceable back.
**Fallback:** 3mm MDF prototype with a cardboard mock-up first.
**Avoid:** paper-faced backing board as a permanent structural panel.

- Design the enclosure **before** the wiring and the panel connector.
- Add a cable exit with strain relief and a fuse holder.
- Keep the diffuser parallel to the print; warped panels show as uneven light.
- Provide access to the driver and the strip harness without desoldering.
- Paint/primer compatibility matters more than colour choice.

---

## 9. Substitution ladder (one-page summary)

| Category | Primary | Fallback | Avoid | Switch trigger |
|---|---|---|---|---|
| Power inlet | USB-C PD trigger 12V | 12V adapter + DC jack | 5V→12V boost for >0.5A | Load >50% of converter rating |
| LED | 5050 12V + diffuser | 2835/COB | 220V strip in handmade box | Standoff <15mm → COB |
| Joining | Solderless connector | Solder + heat-shrink | Pin headers | Joint must be permanent → solder |
| Switch | Ready 12V touch dimmer | TTP223 + MOSFET | TTP223 alone | Load > logic output |
| Diffusion | Opal diffuser 3mm | Tracing paper | Milky acrylic alone | Hotspots at 30cm |
| Adhesive | 3M tape + silicone | Hot glue (prototype) | Glue stick | Temperature >60°C |
| Cutting | Plotter/CNC | Fresh scalpel + ruler | Dull utility knife | >2 identical pieces |
| Enclosure | 6mm MDF/plywood | 3mm MDF + mock-up | Paper-backed board | Span >30cm or permanent |
| Seal/finish | Primer + compatible paint | Matte spray | Cheap gloss on flexible parts | Peeling/fingerprints |

---

## 10. Why choices fail — recurring patterns

1. **Confusing related properties.** Diffusion vs colour temperature; voltage vs power; wire
   gauge vs diameter; "2A module" vs 2A at your input voltage.
2. **Ignoring derating.** A part run at 90–100% of rating is a part that will fail in a closed
   box, not a part that "should work".
3. **Tool capability mismatch.** An 80W unregulated iron for LED pads; a glue stick for a warm
   strip; a dull blade for coated paper.
4. **Interface mismatch.** Logic output driving a load; 8mm connector on 10mm strip; panel
   socket thicker than the panel.
5. **Sequence error.** Wiring before the enclosure; buying the strip before the diffuser
   standoff is known; printing a batch before testing one cut.
6. **Buying in bulk before the spike.** The saving on 10 pieces is worthless if the design
   changes after the first.
7. **Hidden costs.** Connectors, adapters, shipping, storefront minimums, failed experiments.
8. **Unit confusion.** Rial vs Toman; mm vs cm; W/m vs W total.
9. **Solving the symptom, not the cause.** A hotter iron does not fix a bad pad; a bigger
   heatsink does not fix an undersized converter.
10. **No measurement.** Without V/A/°C, every later decision is a guess dressed as experience.
