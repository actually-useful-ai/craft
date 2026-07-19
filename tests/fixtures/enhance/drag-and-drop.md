Decision: for a modern React app, use `@dnd-kit/react` (currently 0.5.0) if its React 18/19 peer requirement matches the app. No files were changed.

### Reuse now

No local React project, dependency manifest, or existing drag-and-drop implementation was provided; local reuse is therefore empty.

Selected reusable target: `@dnd-kit/react`.

- License: MIT; confirm against the project’s license policy.
- Maintenance: upstream lists a release on 13 Apr 2026 and a current multi-framework rewrite.
- Compatibility: package declares peers `react` and `react-dom` `^18 || ^19`; supports both ESM and CommonJS exports.
- Accessibility: upstream documents keyboard, mouse, pointer, and touch sensors; default ARIA attributes, configurable screen-reader instructions, and live regions.
- Evidence checked: 18 Jul 2026 — [package manifest](https://raw.githubusercontent.com/clauderic/dnd-kit/main/packages/react/package.json), [upstream repository](https://github.com/clauderic/dnd-kit).

### Learn from

Use the library’s keyboard/screen-reader primitives, but still provide a non-drag control for reordering (for example, Move up/Move down) and test the final interaction with keyboard and screen reader. WAI-ARIA 1.2 deprecates `aria-grabbed` and `aria-dropeffect`; do not recreate the obsolete ARIA drag-and-drop pattern. Evidence checked: 18 Jul 2026 — [dnd-kit](https://github.com/clauderic/dnd-kit), [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/).

### Conventional vs niche

- Conventional, broadly supported React choice: `@dnd-kit/react` — active upstream, React-specific adapter, modern React 18/19 peers, and documented accessibility support.
- Established specialized alternative: `@atlaskit/pragmatic-drag-and-drop` — framework-agnostic, Apache-2.0, small headless core, and built for large production products. Its optional React accessibility tools need deliberate integration, so it is stronger when native/browser drag behavior or cross-framework portability matters. Evidence checked: 18 Jul 2026 — [package manifest](https://raw.githubusercontent.com/atlassian/pragmatic-drag-and-drop/main/packages/core/package.json), [official documentation/repository](https://github.com/atlassian/pragmatic-drag-and-drop).

### Considered and skipped

- `@atlaskit/pragmatic-drag-and-drop`: viable fallback, not first choice for an unspecified React interaction because it is lower-level and its accessibility flow is optional/custom. License Apache-2.0; core has no React peer dependency, so actual React integration and accessibility acceptance remain to validate. Maintained through Atlassian’s internal-monorepo mirror, which documents daily public sync and immediate npm publication.
- `react-dnd`: MIT and compatible with React `>=16.14`, but the current package manifest is version 16.0.1; its current accessibility behavior was not verified from primary documentation in this review, so it is a lead rather than a recommendation. Evidence checked: 18 Jul 2026 — [manifest](https://raw.githubusercontent.com/react-dnd/react-dnd/main/packages/react-dnd/package.json), [license](https://github.com/react-dnd/react-dnd/blob/main/LICENSE).
- `@hello-pangea/dnd`: focused, accessible list reordering with React 18/19 peers and Apache-2.0 license, but its latest verified release is 18.0.1 from 9 Feb 2025. Skip unless the feature is strictly list reordering and its model is preferred. Evidence checked: 18 Jul 2026 — [manifest](https://raw.githubusercontent.com/hello-pangea/dnd/main/package.json), [release](https://github.com/react-forked/dnd/releases).
- `react-beautiful-dnd`: reject. Atlassian archived it on 18 Aug 2025 and marks it deprecated on npm. Evidence checked: 18 Jul 2026 — [archived upstream repository](https://github.com/atlassian/react-beautiful-dnd).

### Gap

The target project’s React version, package manager, SSR/browser support, license policy, interaction shape, and existing dependencies are unknown. The smallest required construction is one dependency addition plus a constrained sortable interaction; validate React 18/19 compatibility, keyboard/screen-reader behavior, touch behavior, and a non-drag reorder path before merging.

### Handoff

`/craft:compose`: add `@dnd-kit/react` only after confirming React 18 or 19 in the project manifest. Implement the smallest sortable interaction using its keyboard and live-region support, retain button-based reordering, and run keyboard, screen-reader, touch, and target-browser checks.
