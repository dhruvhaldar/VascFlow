## 2024-05-24 - Async 3D Rendering Feedback
**Learning:** Loading and parsing large `.vtp` files with `vtk.js` in the `Viewer.svelte` component blocks the main thread and can take a perceptible amount of time. Previously, this process happened silently, leaving screen readers unaware of the background activity and sighted users wondering if the application had hung.
**Action:** When adding loading states for heavy client-side processing (like 3D rendering), always pair the visual indicator with an ARIA live region (`role="status" aria-live="polite"`) to ensure the transition from "uploading" to "rendering" is explicitly announced. Additionally, disabling the initial file input during this entire flow prevents confusing race conditions from double-uploads.

## 2024-05-24 - Svelte ARIA Strictness and Tabpanels
**Learning:** Svelte's compiler strictly enforces native HTML ARIA constraints (`a11y_no_noninteractive_element_to_interactive_role`). Assigning an interactive role like `role="tablist"` to a semantic non-interactive element like `<nav>` throws an error. Neutral elements like `<div>` should be used instead. Additionally, elements with `role="tabpanel"` require `tabindex="0"` to be keyboard focusable, ensuring accessibility for their nested contents.
**Action:** When implementing custom tab patterns, always use a plain `<div>` for the `tablist` container rather than semantic tags like `<nav>` or `<ul>`. Always ensure the corresponding `tabpanel` has `tabindex="0"` to maintain proper document tab order.

## 2026-04-14 - DOM Isolation for WebGL Empty States
**Learning:** When adding empty states or loaders inside containers managed by third-party WebGL libraries (like `vtk.js`), the library will often clear or overwrite the container's inner HTML upon initialization. Mixing Svelte conditional blocks with WebGL canvas mounts in the same element leads to visual glitches or missing UI.
**Action:** Always extract the `bind:this` canvas mount point to a dedicated inner sibling element (e.g., `<div class="canvas-mount">`) separate from the Svelte UI overlays (like empty states) to ensure DOM isolation.

## 2024-05-24 - Form Input Validation
**Learning:** In Svelte applications utilizing semantic `<form on:submit|preventDefault={...}>` handlers, it is essential to leverage native browser validation to enforce constraints like requiring values. Adding the `required` attribute to constituent `<input>` and `<select>` elements prevents incomplete submissions entirely within the browser, providing localized tooltip feedback before the JS event is even triggered.
**Action:** When creating form flows, always pair the `<form>` wrapper with the HTML5 `required` attribute on essential input fields to gracefully block incomplete data submissions and provide native inline error notifications.

## 2024-05-24 - Masking Internal System URLs in UI
**Learning:** Exposing internal system identifiers like generated UUIDs or `blob:http://...` URLs in the UI (specifically within `aria-live` regions or status text) creates a poor experience for all users, but is especially detrimental to screen reader accessibility. Screen readers will painfully read out the entire noisy URL character-by-character, obscuring the actual state context.
**Action:** Always map internal system references (like generated backend filenames or Blob URLs) to the user's original context (e.g., the original uploaded filename) when displaying status information. Provide human-readable text fallbacks if the original context is temporarily unavailable.
## 2024-04-19 - Removed Empty Readonly Textarea from Accessibility Tree
**Learning:** When using an absolute-positioned "empty state" overlay to cover a readonly `<textarea>`, the underlying textarea remains in the DOM. This causes screen readers to still read the empty textarea and allows keyboard users to tab into a visually obscured, useless element.
**Action:** When implementing full-coverage empty states over interactive elements, explicitly remove the underlying elements from the focus order (`tabindex="-1"`) and the accessibility tree (`aria-hidden="true"`).

## 2024-05-24 - Accessible File Drop Zones
**Learning:** Adding drag-and-drop file upload capabilities dramatically improves UX on desktop, but entirely replacing standard inputs with custom div-based drop zones often breaks keyboard and screen-reader accessibility.
**Action:** When creating drag-and-drop file areas, always implement them as a progressive enhancement around a standard, visually exposed `<input type="file">`. This ensures users who rely on keyboard navigation or screen readers can still easily activate the standard file browser dialog without losing functionality.
