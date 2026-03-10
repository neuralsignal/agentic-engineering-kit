---
name: frontend-design
description: Frontend design aesthetics and UI/UX guidance — typography, color, motion, spatial composition, and component architecture patterns for web interfaces.
---

# Frontend Design Skill

**Trigger:** Use this skill when asked to build web components, pages, apps, posters, dashboards, landing pages, or when styling/beautifying any web UI.

## Locations

- `skills/frontend-design/` — this skill (guidance only, no scripts)

---

## Design Philosophy

Great web interfaces are **designed**, not assembled. They have a point of view. They use restraint. They make the user feel something.

The goal is not "clean" or "modern" — it is *specific*. Every visual decision (typeface, spacing, color, motion) should serve the product's character. Generic defaults produce forgettable interfaces.

---

## Typography

- Use **one typeface family** with distinct weights. Two at most (display + body).
- Avoid Inter, Roboto, and system-ui as your primary display face — they signal "default." Use them only for data-dense UIs where neutrality is the feature (e.g., dashboards, code editors).
- Prefer **optical sizing**: large headlines at light/thin weights, body text at regular/medium.
- Line height: 1.1–1.2× for headlines; 1.5–1.6× for body.
- Letter spacing: tight (−0.02em to −0.04em) for large headlines; default or slightly loose for body.
- Cap line-length at 60–70 characters for readable prose. Data tables can be wider.
- Type scale: use a modular scale (1.25× or 1.333×), not arbitrary sizes.

---

## Color

- Derive from **one primary hue**. Build a scale (50–950) from it. Neutral grays should lean into the primary hue (warm or cool), not be pure gray.
- Limit the palette: one primary, one accent (optionally complementary), semantic colors (success/warning/error), and neutrals.
- Avoid default purple gradients (#6366f1→#8b5cf6) — they appear in every AI-generated UI.
- Dark mode is not "invert everything." Recalibrate contrast ratios independently. Elevated surfaces are *lighter*, not darker.
- Text contrast: 4.5:1 minimum for body (WCAG AA); 3:1 minimum for large/bold text.
- Use color to convey meaning, not just decoration. If two different things share a color, the user assumes they're related.

---

## Spatial Composition

- Establish a **spacing scale** and stick to it. 4px base, powers of 2 (4, 8, 16, 24, 32, 48, 64, 96).
- Whitespace is a design element, not wasted space. Use generous padding to signal importance.
- Visual hierarchy through **size contrast**, not just color. The most important element should be noticeably larger.
- Grid: 12 columns for complex layouts; 4 or 8 columns for focused content. Always define gutters explicitly.
- Alignment: align to an invisible grid. Mixed alignment (some left, some center) looks accidental unless intentional.
- Avoid cards inside cards. Nested containers create visual noise; flatten the hierarchy where possible.

---

## Motion

- Motion should feel **physical**: ease-in for exits (things leaving need inertia), ease-out for entrances (things arriving need deceleration).
- Duration guide: micro-interactions 100–200ms; panel transitions 200–350ms; page transitions 300–500ms.
- Use `cubic-bezier` curves, not linear. Never animate `height` — animate `transform: scaleY` or `max-height` with overflow hidden.
- Animate **one property** at a time per element. Simultaneous scale + fade + translate looks chaotic.
- Respect `prefers-reduced-motion`. Wrap all non-essential animations in a media query.
- Motion should reinforce causality: a deleted item shrinks away; a new item expands in; a navigation moves directionally.

---

## Anti-Patterns (AI Slop Warning)

These patterns appear in the majority of AI-generated interfaces and immediately signal "AI made this":

- **Inter/Roboto everywhere** — use a typeface with character
- **Purple/blue gradient backgrounds** (`#6366f1` → `#8b5cf6`) — overused to the point of parody
- **Uniform rounded corners** (everything `rounded-lg`) — vary radius by element size; large containers can be sharp
- **Cards for everything** — not every piece of content needs a box and a shadow
- **`text-gray-500` body text** — too low contrast; use `text-gray-700` or better on white
- **Icon + label repeated 6 times in a grid** — this is not a design, it is a list
- **Glow effects and glassmorphism** — 2021 trends; avoid unless the product aesthetic explicitly calls for it
- **Centered everything** — left-align body text; center only for short, headline-style copy
- **Padding-less containers flush to screen edge** — always give breathing room

---

## Component Architecture (Vercel Composition Patterns)

### Avoid Boolean Props That Encode Variants

```tsx
// BAD — boolean props create implicit state machines
<Button primary disabled large />

// GOOD — explicit variant enum
<Button variant="primary" size="large" disabled />
```

### Compound Components for Complex UI

When a component has multiple related sub-parts, use compound components instead of a monolithic prop API:

```tsx
// BAD — prop drilling hell
<Dialog title="Confirm" body="..." footer={<><Button>Cancel</Button><Button>OK</Button></>} />

// GOOD — compound components
<Dialog>
  <Dialog.Title>Confirm</Dialog.Title>
  <Dialog.Body>...</Dialog.Body>
  <Dialog.Footer>
    <Button>Cancel</Button>
    <Button variant="primary">OK</Button>
  </Dialog.Footer>
</Dialog>
```

### Context Interfaces

Define explicit TypeScript interfaces for context values. Never pass raw state through context without typing it.

```tsx
interface ThemeContextValue {
  theme: "light" | "dark";
  setTheme: (theme: "light" | "dark") => void;
}
const ThemeContext = createContext<ThemeContextValue | null>(null);
```

### React 19 Notes

- `use(promise)` replaces `useEffect` + `useState` for data fetching in most cases
- Server Components: keep data fetching in server components; pass serializable props to client components
- `useOptimistic` for instant UI feedback on mutations
- `useFormStatus` inside form children to read pending state without prop drilling

---

## Web Interface Guidelines Reference

For a comprehensive, up-to-date code review checklist, fetch the live Vercel guidelines:

```bash
curl -sL https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

These guidelines cover: layout hierarchy, content density, interactive states, accessibility, and responsive behavior. Use them when reviewing or critiquing an existing interface.

---

## Checklist Before Shipping

- [ ] Typography: is the typeface choice intentional? Does weight contrast work at all sizes?
- [ ] Color: does the palette derive from one primary hue? Is contrast WCAG AA compliant?
- [ ] Spacing: is there a consistent scale? Is there enough whitespace around focal elements?
- [ ] Motion: do transitions feel physical? Is `prefers-reduced-motion` respected?
- [ ] No AI slop: none of the anti-patterns above are present
- [ ] Component API: no boolean props encoding variants; compound components where needed
- [ ] Accessibility: keyboard nav works; focus rings are visible; ARIA labels on icon-only buttons
