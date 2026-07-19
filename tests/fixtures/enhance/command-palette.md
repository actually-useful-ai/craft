## Enhance — dense command palette

**Decision:** Do not let the review deadline force a remembered custom pattern. Build one modal palette with a labeled filtering input, flat grouped results, visible keyboard shortcuts where available, and `Arrow`/`Enter`/`Escape` behavior. Defer multi-mode syntax, nested palettes, and persistent history until the first palette is proven.

Evidence checked **2026-07-18**. I searched `<project-root>` for palette, combobox, dialog, and command-menu precedents; it has no implementation or package manifest. `<configured-shared-root>` is unavailable in this environment, so it is not evidence of reuse. I also checked current canonical standards, package registry/repository sources, and live product documentation. No files were changed.

### Reuse now

No local component or dependency is reusable now.

If the target is a React 18 client UI, `cmdk` is a conditional reuse target: it is MIT-licensed, has a current v1.1.1 release dated March 2025, is an unstyled command-menu/combobox component, and documents automated filtering, grouping, empty states, and dialog use. Its declared accessibility evidence is project-level VoiceOver/DevTools testing, not validation of this product. It requires React 18 and is not a React Server Component, so it cannot be selected until the target runtime is known. [cmdk repository](https://github.com/dip/cmdk), [cmdk registry record](https://www.npmjs.com/package/cmdk) — evidence checked 2026-07-18.

### Learn from

- GitHub’s live palette uses an everywhere-available shortcut, context-aware suggestions, editable scope, arrow-key selection, `Enter` to execute, and `Escape` to close. Take the context-aware filtering and predictable keyboard behavior; do not copy its multi-scope grammar for the initial build. [GitHub Command Palette](https://docs.github.com/en/get-started/accessibility/github-command-palette) — evidence checked 2026-07-18.

- VS Code demonstrates the dense-tool convention of clear category-prefixed command names and visible shortcut affordances. Its fuzzy search is a useful later enhancement; its mode prefixes and multi-picker system are beyond the smallest first build. [VS Code Command Palette guidance](https://code.visualstudio.com/api/ux-guidelines/command-palette), [VS Code UI documentation](https://code.visualstudio.com/docs/editing/userinterface) — evidence checked 2026-07-18.

- For the filtered field, follow the W3C combobox pattern: retain DOM focus on the input while updating the active result, and support the documented arrow, `Enter`, and `Escape` interactions. ARIA 1.3 requires the combobox to have an accessible name and `aria-expanded`; it defines the valid `aria-activedescendant` relationship. [WAI-ARIA APG Combobox Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/), [WAI-ARIA 1.3](https://www.w3.org/TR/wai-aria-1.3/) — evidence checked 2026-07-18.

- If the palette blocks the page, follow the modal-dialog pattern: focus enters the palette, remains inside it while open, `Escape` closes it, and focus returns logically to the invoker. WCAG 2.2 additionally makes keyboard operation, focus order/visibility, focus-not-obscured, and name/role/value relevant. This is accessibility evidence, not an accessibility audit. [WAI-ARIA APG Modal Dialog Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/), [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — evidence checked 2026-07-18.

### Conventional vs niche

**Conventional:** one focused overlay, an immediately usable filter field, a single active result, arrow-key traversal, `Enter` execution, `Escape` dismissal, grouped commands, and shortcut display. This is independently represented by the maintained live GitHub and VS Code products and is directly covered by W3C combobox/dialog guidance.

**Niche for a first release:** command-language prefixes (`>`, `#`, `@`, `/`), editable scope breadcrumbs, persistent MRU ranking, nested pages, and user-configurable global keybindings. GitHub and VS Code show these in mature, broader-scope products, but they are not a prerequisite for a dense, discoverable palette and add state, documentation, and keyboard edge cases.

### Considered and skipped

- **Existing local/shared component:** skipped because no local palette implementation exists and the configured shared location could not be read. No reuse claim is being made.

- **`cmdk`:** deferred, not rejected. License is MIT; maintenance signal is v1.1.1 released March 2025; compatibility is React 18 client-only; accessibility evidence is upstream self-reporting plus its dialog composition. The project runtime is unknown, so adding it now would be premature. [Repository](https://github.com/dip/cmdk), [package record](https://www.npmjs.com/package/cmdk) — checked 2026-07-18.

- **Radix Dialog:** deferred as a possible React-only shell. It is MIT-licensed, actively documented, and its dialog documentation covers focus and `Escape`; it does not supply the palette’s filtering/result model. [Radix Dialog](https://www.radix-ui.com/primitives/docs/components/dialog), [repository](https://github.com/radix-ui/primitives) — checked 2026-07-18.

- **Native `<dialog>`:** not selected before knowing browser/support constraints and desired overlay behavior. It is a dependency-free, widely available platform option with useful modal focus behavior, but it does not implement the required combobox/result semantics. [MDN `<dialog>` reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog) — checked 2026-07-18.

- **`react-cmdk`:** skipped as a recommendation: its registry record shows the last publish was three years ago and only two dependents, weaker maintenance/adoption signals than `cmdk`; license and target-project compatibility were not independently verified. [react-cmdk registry record](https://www.npmjs.com/package/react-cmdk) — checked 2026-07-18.

### Gap

The target framework, command inventory, action authorization rules, and expected result count are unknown. The smallest construction still needed is a command registry (`id`, label, category, keywords, optional shortcut, enabled state, action) plus a modal filter-and-result view that keeps the selected item scrolled into view.

Validate the framework choice before selecting a dependency; then validate opening shortcut conflicts, focus return, keyboard traversal, empty/disabled results, and actual screen-reader announcements in the rendered product. A dedicated accessibility or intentional-UX review should cover those real-interface checks rather than treating this reconnaissance as an audit.

### Handoff

Hand to `/craft:compose` with the selected gap: implement the conventional single-level modal palette first. If the target is React 18 client-side, use `cmdk` as the reuse target; otherwise construct the native dialog/combobox behavior from the cited W3C patterns. Keep prefixes, MRU, nested flows, and customizable shortcuts out of the first build pending usability validation.
