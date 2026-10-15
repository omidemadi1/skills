# Design System Mapping

When the brief matches a known design system, use the official package. One system per project. Never mix.

## When to Use Official Packages

| Brief reads as | Package | Install |
|---|---|---|
| Microsoft/enterprise SaaS | `@fluentui/react-components` | `npm install @fluentui/react-components` |
| Material-flavored product | `@material/web` + Material 3 | `npm install @material/web` |
| IBM/Carbon B2B | `@carbon/react` + `@carbon/styles` | `npm install @carbon/react @carbon/styles` |
| Shopify app surfaces | Polaris web components | CDN via `<script src="https://cdn.shopify.com/shopifycloud/polaris.js">` |
| Atlassian/Jira-style | `@atlaskit/*` + tokens | `yarn add @atlaskit/css-reset @atlaskit/tokens @atlaskit/button @atlaskit/badge` |
| GitHub/devtool/community | `@primer/react-brand` | `npm install @primer/react-brand` |
| Public-sector UK | `govuk-frontend` | `npm install govuk-frontend` |
| US public-sector/trust-first | `uswds` | `npm install uswds` |
| Fast local-business/agency MVP | Bootstrap 5.3 | `npm install bootstrap` |
| Modern accessible React | `@radix-ui/themes` | `npm install @radix-ui/themes` |
| Modern SaaS (own components) | shadcn/ui | `npx shadcn@latest init` then `npx shadcn@latest add button card badge separator input` |
| Tailwind-based modern SaaS | Tailwind v4 utilities + `dark:` variant | Default for indie + small team builds |

## Honesty Rules

- If brief reads as one of these systems, install and use the **official** package
- Do not recreate its CSS by hand
- Do not import a system's tokens but override 90% of them
- **One system per project.** Do not mix Fluent with Carbon, or shadcn into Material 3

## When the Brief is an Aesthetic, Not a System

No official package exists. Build with native CSS + Tailwind + maintained component library. Be honest in code comments about what is borrowed inspiration vs. official material.

| Aesthetic | Implementation |
|---|---|
| Glassmorphism / "frosted glass" | `backdrop-filter`, layered borders, highlight overlays. Solid-fill fallback for `prefers-reduced-transparency` |
| Bento (Apple-style tile grids) | CSS Grid with mixed cell sizes. No single library owns this |
| Brutalism | Native CSS, monospace, raw borders. No library |
| Editorial / magazine | Serif type, asymmetric grid, generous whitespace. No library |
| Dark tech / hacker | Mono + accent neon, terminal motifs. No library |
| Aurora / mesh gradients | SVG or layered radial gradients. No library |
| Kinetic typography | Native CSS animations, scroll-driven animations, GSAP for hijacks. No library |
| Apple Liquid Glass | Apple platforms only. Web = `backdrop-filter` + layered borders + highlights. Label as approximation |

## Apple Liquid Glass Web Approximation

```css
.liquid-glass-web-approx {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 999px;
  border: 1px solid rgb(255 255 255 / .32);
  background:
    linear-gradient(135deg, rgb(255 255 255 / .30), rgb(255 255 255 / .08)),
    rgb(255 255 255 / .12);
  backdrop-filter: blur(24px) saturate(180%) contrast(1.05);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / .48),
    inset 0 -1px 0 rgb(255 255 255 / .12),
    0 18px 60px rgb(0 0 0 / .18);
}

@media (prefers-color-scheme: dark) {
  .liquid-glass-web-approx {
    border-color: rgb(255 255 255 / .18);
    background:
      linear-gradient(135deg, rgb(255 255 255 / .16), rgb(255 255 255 / .04)),
      rgb(15 23 42 / .42);
    box-shadow:
      inset 0 1px 0 rgb(255 255 255 / .22),
      0 18px 60px rgb(0 0 0 / .42);
  }
}

@media (prefers-reduced-transparency: reduce) {
  .liquid-glass-web-approx {
    background: rgb(255 255 255 / .96);
    backdrop-filter: none;
  }
}
```

## Canonical Documentation Links

- Material: https://material-web.dev/theming/material-theming/
- Fluent: https://fluent2.microsoft.design/get-started/develop
- Carbon: https://carbondesignsystem.com/
- Polaris: https://polaris-react.shopify.com/components
- Atlassian: https://atlassian.design/get-started/develop
- Primer: https://primer.style/
- GOV.UK: https://design-system.service.gov.uk/
- USWDS: https://designsystem.digital.gov/
- Radix: https://www.radix-ui.com/themes/docs/components/theme
- shadcn: https://ui.shadcn.com/docs
- Tailwind: https://tailwindcss.com/docs/dark-mode
