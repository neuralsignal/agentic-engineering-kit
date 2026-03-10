---
name: web-artifacts-builder
description: Build complex React artifacts (React + TypeScript + Tailwind CSS 3 + shadcn/ui, 40+ components pre-installed) and bundle them to a single self-contained HTML file for display in conversation.
---

# Web Artifacts Builder Skill

**Trigger:** Use when asked to build interactive React-based UI components, dashboards, data visualizations, or any web artifact that needs to be displayed as a self-contained single-file HTML in conversation.

Also consult `skills/frontend-design/SKILL.md` for design aesthetics before writing any component.

## Locations

- `skills/web-artifacts-builder/scripts/init-artifact.sh` — scaffolds a new React + Vite + Tailwind + shadcn/ui project
- `skills/web-artifacts-builder/scripts/bundle-artifact.sh` — bundles the project to a single `bundle.html` file
- `skills/web-artifacts-builder/scripts/shadcn-components.tar.gz` — pre-built shadcn/ui components (40+)

## Prerequisites

Node.js ≥ 18 and pnpm must be available. The init script auto-installs pnpm via `npm install -g pnpm` if missing.

Check:
```bash
node --version   # must be v18+
# pnpm auto-installed by init script if missing
```

## Running Scripts

```bash
# Step 1: Scaffold a new project
bash skills/web-artifacts-builder/scripts/init-artifact.sh <project-name>

# Step 2: Build your component in src/App.tsx

# Step 3: Bundle to single HTML
cd <project-name>
bash ../skills/web-artifacts-builder/scripts/bundle-artifact.sh
# Output: <project-name>/bundle.html
```

## Stack Produced

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | UI framework |
| TypeScript | Latest | Type safety |
| Vite | Latest (5.4.11 for Node 18) | Dev server + HMR |
| Tailwind CSS | 3.4.1 | Utility CSS |
| shadcn/ui | 40+ components | Pre-built UI primitives |
| Parcel | Latest | Single-file bundler |
| html-inline | Latest | Inlines all assets into one HTML |

## Included shadcn/ui Components

accordion, alert, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input, label, menubar, navigation-menu, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, skeleton, slider, sonner, switch, table, tabs, textarea, toast, toggle, toggle-group, tooltip

Import pattern:
```tsx
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'
```

## Workflow

1. **Scaffold** — run `init-artifact.sh <project-name>`. Creates a fully configured project.
2. **Implement** — edit `src/App.tsx` (and create additional components in `src/`). The entire artifact lives in one React app.
3. **Dev server** — optionally run `cd <project-name> && pnpm dev` to preview locally.
4. **Bundle** — run `bundle-artifact.sh` from inside the project directory. Outputs `bundle.html`.
5. **Display** — the `bundle.html` is a fully self-contained single HTML file. Read it and include it as an artifact in conversation.

## Performance Guidelines (from Vercel React Best Practices)

**Avoid waterfalls.** Fetch data at the route level, not inside deeply nested components. Parallel fetch with `Promise.all`. Never trigger a fetch inside a useEffect that itself depends on another fetch result.

**Minimize bundle size.** Tree-shake lodash (`import { debounce } from 'lodash-es'` not `import _ from 'lodash'`). Lazy-load heavy components with `React.lazy` + `Suspense`.

**Prevent unnecessary re-renders.** Memoize expensive components with `React.memo`. Memoize callbacks with `useCallback` when passing to memoized children. Use `useMemo` for expensive derived values, not for cheap calculations.

**State colocation.** Keep state as close to where it's used as possible. Global state (context, Zustand) only for genuinely shared state. Lifting state too high causes unnecessary re-renders of unrelated subtrees.

**Keys in lists.** Always use stable, unique keys in `.map()` — never array indices for dynamic lists.

**Event delegation.** Prefer event handlers at the container level for long lists (e.g., table rows) rather than per-item handlers.

## Anti-AI-Slop Warning

Read `skills/frontend-design/SKILL.md` before writing any component. Specifically:
- Do NOT use default Inter/Roboto for display headings
- Do NOT use the purple/blue gradient (`#6366f1` → `#8b5cf6`)
- Do NOT give every container uniform `rounded-lg`
- Do NOT use `text-gray-500` for body text (too low contrast)
- Every design choice should be **intentional**, not whatever Tailwind defaults to

---

## Example: Minimal App.tsx

```tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Counter</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-4xl font-bold tabular-nums text-center">{count}</p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setCount(c => c - 1)}>−</Button>
            <Button className="flex-1" onClick={() => setCount(c => c + 1)}>+</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```
