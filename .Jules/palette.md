## 2024-05-24 - [Svelte Interactive Roles on Structural Elements]
**Learning:** Svelte's accessibility compiler enforces strict native HTML ARIA constraints (`a11y_no_noninteractive_element_to_interactive_role`). Applying `role="tablist"` to a semantic non-interactive element like `<nav>` violates this constraint.
**Action:** When implementing interactive ARIA patterns (like tabs) in Svelte, use structurally neutral elements (like `<div>` with descriptive classes) instead of semantic tags, and ensure the corresponding target containers (like `role="tabpanel"`) are given `tabindex="0"` for keyboard focusability.

## 2024-05-25 - [Dynamic Context for List Item Actions]
**Learning:** For repetitive list items with action buttons (like delete buttons), using static ARIA labels (e.g., `aria-label="Remove boundary condition"`) fails to provide screen reader users context about *which* item they are about to delete. Additionally, list elements that are dynamically updated need an `aria-live` region.
**Action:** Always use dynamic, contextual ARIA labels (e.g., `aria-label="Remove boundary condition for {bc.face_name}"`) by interpolating item data. Also, wrap the dynamic list and its empty state in a `<div aria-live="polite">` so additions/removals are announced.
