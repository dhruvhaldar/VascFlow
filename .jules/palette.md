## 2024-05-24 - Async 3D Rendering Feedback
**Learning:** Loading and parsing large `.vtp` files with `vtk.js` in the `Viewer.svelte` component blocks the main thread and can take a perceptible amount of time. Previously, this process happened silently, leaving screen readers unaware of the background activity and sighted users wondering if the application had hung.
**Action:** When adding loading states for heavy client-side processing (like 3D rendering), always pair the visual indicator with an ARIA live region (`role="status" aria-live="polite"`) to ensure the transition from "uploading" to "rendering" is explicitly announced. Additionally, disabling the initial file input during this entire flow prevents confusing race conditions from double-uploads.

## 2024-05-24 - Svelte ARIA Strictness and Tabpanels
**Learning:** Svelte's compiler strictly enforces native HTML ARIA constraints (`a11y_no_noninteractive_element_to_interactive_role`). Assigning an interactive role like `role="tablist"` to a semantic non-interactive element like `<nav>` throws an error. Neutral elements like `<div>` should be used instead. Additionally, elements with `role="tabpanel"` require `tabindex="0"` to be keyboard focusable, ensuring accessibility for their nested contents.
**Action:** When implementing custom tab patterns, always use a plain `<div>` for the `tablist` container rather than semantic tags like `<nav>` or `<ul>`. Always ensure the corresponding `tabpanel` has `tabindex="0"` to maintain proper document tab order.

## 2024-05-24 - Contextual ARIA Labels in Lists
**Learning:** When rendering lists of items with identical interactive elements (like 'Remove' buttons in the Boundary Conditions list), standard `aria-label="Remove boundary condition"` is insufficient for screen reader users as they cannot distinguish which item will be removed when navigating by buttons.
**Action:** Always inject the unique identifier (like `{bc.face_name}`) into the `aria-label` to provide necessary context (e.g. `aria-label="Remove boundary condition for {bc.face_name}"`).
