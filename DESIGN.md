---
version: alpha
name: Warm Systems Portfolio
description: A warm editorial portfolio for an AI and backend engineer, balancing technical credibility with an approachable personal voice.
colors:
  primary: "#10221b"
  on-primary: "#fff9f0"
  secondary: "#2d6656"
  accent: "#bd6c3d"
  background: "#f7f1e8"
  surface: "#fffaf4"
  text: "#17261f"
  muted: "#5e6a62"
  border: "rgba(23, 38, 31, 0.12)"
typography:
  display-xl:
    fontFamily: "Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif"
    fontSize: 4.9rem
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: -0.03em
  display-md:
    fontFamily: "Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif"
    fontSize: 3.5rem
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: -0.03em
  heading-sm:
    fontFamily: "Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif"
    fontSize: 1.3rem
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Trebuchet MS, Gill Sans, Avenir Next, sans-serif"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Trebuchet MS, Gill Sans, Avenir Next, sans-serif"
    fontSize: 0.8rem
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: 0.16em
rounded:
  sm: 14px
  md: 20px
  lg: 28px
  pill: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 64px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: 0.85rem 1.2rem
    height: 3rem
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: 0.85rem 1.2rem
    height: 3rem
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
    padding: 1.5rem
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    padding: 0.55rem 0.9rem
    height: 2.3rem
  navigation:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: 0.95rem 1.2rem
  timeline-marker:
    backgroundColor: "{colors.accent}"
    rounded: "{rounded.pill}"
    size: 0.6rem
  divider:
    backgroundColor: "{colors.border}"
    height: 1px
---

## Overview

Warm Systems Portfolio combines editorial warmth with production-engineering clarity. It should feel like the portfolio of an engineer who can turn prototypes into dependable products: technically precise, calm, approachable, and intentionally crafted.

The visual hierarchy leads with outcomes and judgment, then supports them with tools and implementation details. The site must not resemble a generic dashboard, a neon developer template, or a dense résumé pasted into a webpage.

## Colors

The palette uses warm paper-like neutrals with deep green structure and a restrained clay accent.

- **Primary** is the deepest green. Use it for high-confidence actions, dark panels, and major structural emphasis.
- **Secondary** supports navigation, metadata, links, and technical labels.
- **Accent** is reserved for small moments of emphasis such as timeline markers and decorative highlights. It must not dominate large surfaces.
- **Background** and **surface** create a warm, tactile reading environment. Pure white should be used only as a translucent highlight.
- **Text** is softer than black while retaining strong contrast. **Muted** is for supporting copy, never for critical actions or very small text.

Gradients may blend primary with secondary or use a low-opacity accent glow. They are atmospheric, not informational, and must never reduce text contrast.

## Typography

Display text uses the editorial serif stack to give the portfolio a distinct personal voice. Body text and interface labels use the humanist sans-serif stack for practical readability.

Hero headings should be short, outcome-oriented, and constrained to roughly 12–13 characters per visual line on wide screens. Section headings use the same serif voice at a smaller scale. Labels are uppercase, widely tracked, and concise.

Body copy should generally remain between 45 and 70 characters per line. Avoid long centered paragraphs, overly small metadata, and using uppercase for sentences.

## Layout

The page uses a maximum content width of 1180px. Wide layouts pair a dominant content column with a smaller contextual panel. Repeated content uses three-column grids only when every card remains readable; grids collapse to one column below 1080px.

Use generous section spacing and tighter spacing inside related groups. Cards may vary slightly in radius to create an editorial composition, but they must align to the shared radius scale. Content order must remain meaningful without CSS grid placement.

On screens below 720px, navigation becomes horizontally scrollable, metrics stack vertically, card padding is reduced, and all primary actions retain a minimum touch height of 44px.

## Elevation & Depth

Depth comes from restrained translucent surfaces, soft shadows, and subtle background glows. The default card shadow is `0 18px 60px rgba(21, 30, 25, 0.12)`. Sticky navigation uses a lighter shadow so it does not compete with the content.

Backdrop blur is progressive enhancement. Every surface must remain legible when blur is unavailable. Do not stack multiple strong shadows or create floating elements without a clear hierarchy.

## Shapes

Cards use 20–28px corners, feature panels may extend to 36px, and interactive pills use fully rounded corners. Circular shapes are limited to the portrait, timeline markers, and quiet decorative glows.

Borders are thin and low contrast. Shape communicates grouping and affordance; decorative geometry must remain behind content and ignore pointer events.

## Components

**Navigation:** Sticky, translucent, and compact. Links reveal a restrained underline on hover or keyboard focus. On mobile each link becomes a touch-friendly pill in a horizontally scrollable row.

**Primary button:** Uses the deep-green identity, optionally blending toward secondary green. It carries the highest-priority action and always uses the warm light foreground.

**Secondary button:** Uses a light surface with a visible border. It must remain visually quieter than the primary action.

**Cards:** Use a warm translucent surface, light border, and soft shadow. Card headings state an outcome or area of responsibility; supporting paragraphs explain evidence.

**Chips:** Represent technologies or specialties. They are supporting metadata, not calls to action, and should wrap naturally.

**Timeline:** Dates form a separate column on wide screens. The line and clay markers provide continuity but are removed on narrow screens where the content becomes linear.

**Focus and contact panels:** Dark panels are reserved for a current-focus summary or final contact invitation. Never place two competing dark panels in the same viewport.

**Motion:** Entrance motion is subtle and completes in under one second. Fine-pointer devices may use a restrained spatial-card effect with no more than 3 degrees of rotation per axis, a soft pointer-following highlight, and shallow content depth. The effect must not change layout or obscure text. Touch devices do not use pointer tilt. All nonessential animation, spatial depth, and smooth scrolling are disabled when reduced motion is requested.

## Do's and Don'ts

- Do lead with shipped outcomes, engineering decisions, and user value.
- Do keep Turkish and English pages visually identical in structure and emphasis.
- Do preserve visible keyboard focus and at least WCAG AA text contrast.
- Do keep interactive targets at least 44px tall where practical.
- Do use the shared color, typography, spacing, and radius tokens before adding a new value.
- Don't introduce neon colors, cold blue dashboard styling, or terminal-inspired decoration.
- Don't turn every technology name into a badge; chips should remain secondary to the work.
- Don't add heavy parallax, looping animation, or motion required to understand content.
- Don't apply spatial motion to navigation, forms, or elements whose position communicates state.
- Don't hide important content behind hover-only interactions.
- Don't use decorative gradients behind long-form text unless a solid fallback preserves contrast.
