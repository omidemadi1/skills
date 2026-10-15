# Motion Patterns

## Core Rules

- **Motion must be motivated:** Before adding any animation, ask "what does this communicate?" Valid: hierarchy, storytelling, feedback, state transition. Invalid: "it looked cool"
- **Motion claimed = motion shown:** If `MOTION_INTENSITY > 4`, page must actually move. Static page claiming MOTION_INTENSITY: 7 is broken
- **Marquee max-one-per-page:** Two or more on same page = lazy filler
- **GSAP for pin/scrub only.** Motion (`motion/react`) for everything else
- **Never mix GSAP and Motion in same component tree** — they fight over frames

## Forbidden Animation Patterns

- `window.addEventListener("scroll", ...)` — banned. Runs on every frame, jank-prone
- Custom scroll progress using `window.scrollY` in React state — re-renders every frame
- `requestAnimationFrame` loops touching React state — use `useMotionValue` + `useTransform`
- Half-built motion that breaks (cut-off ScrollTriggers, jumpy enters, missing cleanups)
- Infinite loops on every card — only when section actively benefits from motion

## Allowed Scroll Animations

- Motion's `useScroll()` / `useTransform()` / `useMotionValue()`
- GSAP's `ScrollTrigger`
- `IntersectionObserver`
- CSS `scroll-driven animations` (`animation-timeline: view()`)

## Sticky-Stack Canonical Skeleton

```tsx
"use client";
import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function StickyStack({ cards }: { cards: React.ReactNode[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    if (reduce || !ref.current) return;
    const ctx = gsap.context(() => {
      const cardEls = gsap.utils.toArray<HTMLElement>(".stack-card");
      cardEls.forEach((card, i) => {
        if (i === cardEls.length - 1) return;
        ScrollTrigger.create({
          trigger: card,
          start: "top top",                // pin at viewport top
          endTrigger: cardEls[cardEls.length - 1],
          end: "top top",
          pin: true,
          pinSpacing: false,
        });
        gsap.to(card, {
          scale: 0.92,
          opacity: 0.55,
          ease: "none",
          scrollTrigger: {
            trigger: cardEls[i + 1],
            start: "top bottom",
            end: "top top",
            scrub: true,
          },
        });
      });
    }, ref);
    return () => ctx.revert();
  }, [reduce]);

  return (
    <div ref={ref} className="relative">
      {cards.map((card, i) => (
        <div key={i} className="stack-card sticky top-0 min-h-[100dvh] flex items-center justify-center">
          {card}
        </div>
      ))}
    </div>
  );
}
```

**Critical:** `start: "top top"`, `pin: true`, scale/opacity driven by NEXT card's trigger.

## Horizontal-Pan Canonical Skeleton

```tsx
"use client";
import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function HorizontalPan({ children }: { children: React.ReactNode }) {
  const wrap = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    if (reduce || !wrap.current || !track.current) return;
    const ctx = gsap.context(() => {
      const distance = track.current!.scrollWidth - window.innerWidth;
      gsap.to(track.current, {
        x: -distance,
        ease: "none",
        scrollTrigger: {
          trigger: wrap.current,
          start: "top top",                // pin at viewport top
          end: () => `+=${distance}`,     // scroll = horizontal travel needed
          pin: true,
          scrub: 1,
          invalidateOnRefresh: true,
        },
      });
    }, wrap);
    return () => ctx.revert();
  }, [reduce]);

  return (
    <section ref={wrap} className="relative overflow-hidden">
      <div ref={track} className="flex h-[100dvh] items-center">
        {children}
      </div>
    </section>
  );
}
```

**Critical:** `start: "top top"`, `pin: true`, `end: "+=${distance}"`, `scrub: 1`.

## Scroll-Reveal Stagger (lighter alternative)

For simple "items appear on scroll" (no pinning), prefer Motion's `whileInView` over GSAP:

```tsx
"use client";
import { motion, useReducedMotion } from "motion/react";

export function RevealStagger({ items }: { items: string[] }) {
  const reduce = useReducedMotion();
  return (
    <ul className="grid gap-6">
      {items.map((item, i) => (
        <motion.li
          key={item}
          initial={reduce ? false : { opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
        >
          {item}
        </motion.li>
      ))}
    </ul>
  );
}
```

## Reduced Motion (mandatory for MOTION > 3)

- In Motion: wrap with `useReducedMotion()` and degrade to static
- In CSS: gate behind `@media (prefers-reduced-motion: no-preference)` or provide override under `@media (prefers-reduced-motion: reduce)`
- Infinite loops, parallax, scroll-hijack, magnetic physics MUST collapse to static/instant

## Interactive UI States

- **Loading:** Skeletal loaders matching final layout shape. No generic circular spinners
- **Empty States:** Beautifully composed; indicate how to populate
- **Error States:** Clear, inline (forms), or contextual (toasts for transient only)
- **Tactile Feedback:** On `:active`, use `-translate-y-[1px]` or `scale-[0.98]` for physical push feel

## Hardware Acceleration

- Animate ONLY `transform` and `opacity`. Never `top`, `left`, `width`, `height`
- `will-change: transform` sparingly — only on elements that will actually animate
