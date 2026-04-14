## 2024-05-24 - Async 3D Rendering Feedback
**Learning:** Loading and parsing large `.vtp` files with `vtk.js` in the `Viewer.svelte` component blocks the main thread and can take a perceptible amount of time. Previously, this process happened silently, leaving screen readers unaware of the background activity and sighted users wondering if the application had hung.
**Action:** When adding loading states for heavy client-side processing (like 3D rendering), always pair the visual indicator with an ARIA live region (`role="status" aria-live="polite"`) to ensure the transition from "uploading" to "rendering" is explicitly announced. Additionally, disabling the initial file input during this entire flow prevents confusing race conditions from double-uploads.

## 2024-05-24 - Svelte ARIA Strictness and Tabpanels
**Learning:** Svelte's compiler strictly enforces native HTML ARIA constraints (`a11y_no_noninteractive_element_to_interactive_role`). Assigning an interactive role like `role="tablist"` to a semantic non-interactive element like `<nav>` throws an error. Neutral elements like `<div>` should be used instead. Additionally, elements with `role="tabpanel"` require `tabindex="0"` to be keyboard focusable, ensuring accessibility for their nested contents.
**Action:** When implementing custom tab patterns, always use a plain `<div>` for the `tablist` container rather than semantic tags like `<nav>` or `<ul>`. Always ensure the corresponding `tabpanel` has `tabindex="0"` to maintain proper document tab order.

## 2026-04-14 - DOM Isolation for WebGL Empty States
**Learning:** When adding empty states or loaders inside containers managed by third-party WebGL libraries (like `vtk.js`), the library will often clear or overwrite the container's inner HTML upon initialization. Mixing Svelte conditional blocks with WebGL canvas mounts in the same element leads to visual glitches or missing UI.
**Action:** Always extract the `bind:this` canvas mount point to a dedicated inner sibling element (e.g., `<div class="canvas-mount">`) separate from the Svelte UI overlays (like empty states) to ensure DOM isolation.
