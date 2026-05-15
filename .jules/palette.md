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

## 2024-04-24 - Visual Affordances for Destructive Actions
**Learning:** When implementing destructive UI actions like remove or delete buttons within lists, using basic unstyled HTML elements (e.g., `<button>&times;</button>`) lacks the visual affordances necessary to communicate the action's nature. This can lead to accidental clicks or a general lack of confidence when interacting with the interface.
**Action:** Always provide explicit visual feedback for destructive actions by adding semantic classes (like `.remove-btn`) and applying appropriate CSS states (`:hover`, `:focus-visible`) and colors (e.g., shades of red) to enhance the micro-UX and clearly signal the consequence of the action.

## 2024-05-18 - Visible Labels for Inputs
**Learning:** Relying solely on `aria-label` or `placeholder` attributes for input fields (especially numbers and dropdowns) creates an ambiguous experience for sighted users. In forms like BCEditor, seeing a bare number input without context is confusing.
**Action:** Always wrap `<input>` and `<select>` elements in visible `<label>` tags to provide clear, onscreen context for all users, improving both general usability and accessibility.

## 2024-05-24 - Handling Stale Derived State
**Learning:** When displaying derived data (like a generated XML preview) based on user inputs, changing the inputs without regenerating the data leaves the output in a "stale" state. Visually leaving the stale output unaltered is confusing and allows users to copy incorrect data. Furthermore, leaving it in the accessibility tree can mislead screen reader users who might rely on it as the "current" state.
**Action:** When underlying inputs change, always explicitly mark derived preview states as visually outdated (e.g., via an overlay and reduced opacity). Simultaneously, remove the stale interactive elements (like the readonly textarea) from the tab order (`tabindex="-1"`) and accessibility tree (`aria-hidden="true"`) to prevent accidental interaction or misinterpretation by assistive technologies.

## 2024-05-24 - Accessibility Skip Links Targeting
**Learning:** When adding a 'Skip to main content' link for keyboard and screen reader accessibility, simply linking to an ID (e.g., `#main-content`) will visually scroll the page, but may not properly move programmatic focus to semantic elements like `<main>` unless they are natively focusable. If focus doesn't move, the next 'Tab' press will jump back to the top of the document.
**Action:** Always ensure the target element of a skip link (such as `<main id="main-content">`) includes `tabindex="-1"`. This allows it to programmatically receive focus without becoming part of the natural tab order.
## 2024-05-04 - Focus Management on DOM Removal
**Learning:** Removing active interactive elements (like the "Remove BC" button or resetting an active form via `addBC`) causes standard browsers to lose keyboard focus, dropping it back to the `<body>`. This forces keyboard users to tab through the entire document to get back to where they were.
**Action:** Use Svelte's `tick()` alongside component tracking (`bind:this={element}`) to gracefully hand focus back to the primary `<select>` input after the destructive/reset action completes and the DOM has updated.

## 2024-05-19 - Focus Management for Dynamically Disabled Elements
**Learning:** Disabling an active interactive element (like a button after a successful API call or during state changes) causes the browser to lose keyboard focus, dropping it to the `<body>` element. This completely breaks keyboard navigation for screen reader and keyboard-only users.
**Action:** When an interaction results in the currently focused element becoming disabled or removed, explicitly implement programmatic focus management (using Svelte's `tick()`) to gracefully hand off focus to the next logical interactive element (e.g., from a 'Generate' button to a newly appeared 'Copy' button), or restore it when the operation completes.

## 2026-05-11 - [Focus Management after Async Upload]
**Learning:** In Svelte components where interactive elements like `<input type="file">` are disabled during an asynchronous operation (e.g., file upload), the browser loses keyboard focus, dropping it back to the `<body>`.
**Action:** When disabling/re-enabling an interactive element around async work, always use `await tick()` in the `finally` block to wait for the DOM to update (re-enabling the input), and then explicitly restore focus using `.focus()` to maintain seamless keyboard navigation.

## 2026-05-11 - [Visual Loading Indicators on Async Buttons]
**Learning:** Changing button text (e.g., from "Generate XML" to "Generating...") during an asynchronous operation is helpful but often not enough, especially on slower connections or longer processing times. Users may fail to notice a simple text change without accompanying motion, leaving them wondering if the system is actually working.
**Action:** Always pair text changes on async action buttons with explicit, animated visual loading indicators (like an inline spinner). This provides immediate, unmistakable visual feedback that the system is actively processing the request, drastically improving perceived performance and micro-UX.

## 2026-05-11 - [Download Generated Files]
**Learning:** In applications where users configure data and generate files (like an XML simulation file), relying solely on "Copy to clipboard" functionality creates friction. Users ultimately need the file saved on disk. While they can copy and paste into a text editor, a direct "Download" button significantly streamlines their workflow and reduces the chance of manual errors.
**Action:** When a system generates a file based on user input, always provide a direct "Download" button in addition to "Copy to clipboard" functionality. Use a Blob URL with a hidden `<a>` tag to programmatically trigger the download without requiring a server roundtrip.

## 2024-05-10 - Dynamic Tooltips for Disabled Inputs
**Learning:** Disabling an input field during an async operation without context can confuse users as to why it is disabled and when it will be available again.
**Action:** When conditionally disabling inputs (like a file input during processing), dynamically update its `title` attribute to explicitly describe the current status (e.g., "Processing upload, please wait...") to provide immediate, contextual help on hover.

## 2024-05-10 - Reducing Visual Clutter during Processing
**Learning:** Displaying hints (like "or drag and drop a file here") when the corresponding input is disabled and cannot accept interactions adds unnecessary cognitive load and clutter during an active loading state.
**Action:** Hide static interaction hints while the component is in a loading or processing state, ensuring the user's focus is drawn only to the progress indicator and status message.

## 2026-05-11 - [Dynamic Document Titles in SPA]
**Learning:** In a Single Page Application (SPA) or tabbed interface, the URL and visible UI might change, but the `<title>` of the document often remains static. This creates a severe accessibility issue for screen reader users and a usability issue for users with many tabs open, as they lose context of their current location within the application.
**Action:** Always implement dynamic document titles that reflect the current view or active tab state. In Svelte, this is easily achieved using the `<svelte:head><title>...</title></svelte:head>` block bound to the active state variable.

## 2024-05-24 - Layout Shift Mitigation with Transitions
**Learning:** Adding or removing elements from the DOM (like boundary condition list items or file upload status messages) causes jarring layout shifts that disrupt the user's focus and make the interface feel unpolished.
**Action:** Always apply CSS or framework-provided transitions (like Svelte's `transition:slide|local`) to elements that conditionally mount or unmount within the normal document flow to ensure smooth, predictable layout recalculations.

## 2026-05-14 - Explicit Visual Indicators for Required Fields
**Learning:** Relying solely on HTML5 `required` attributes creates an ambiguous experience for sighted users, as they may not know a field is mandatory until they attempt to submit the form or proceed to a next step. This lack of upfront clarity can lead to frustration and disrupted workflows.
**Action:** Always pair HTML5 `required` attributes with an explicit visual indicator (e.g., an asterisk `*` wrapped in a screen-reader hidden span, `<span aria-hidden="true" title="Required">*</span>`) on the corresponding label. This ensures sighted users immediately understand which fields are mandatory before interacting with the form.

## 2026-05-15 - Client-Side Download Visual Feedback
**Learning:** When users trigger local browser downloads via JavaScript (e.g., creating a Blob URL and programmatically clicking an anchor tag), the action is invisible to the application state, leading to a lack of immediate UI feedback. In a React/Svelte SPA, this can make the button feel unresponsive.
**Action:** Treat local downloads similarly to 'Copy to Clipboard' actions. Introduce a temporary (e.g., 2 second) state change that updates the button text to 'Downloaded!', applies a success styling class, and uses `aria-live="polite"` to ensure the action is confirmed for both sighted and screen-reader users.
