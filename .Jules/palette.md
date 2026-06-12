## 2024-05-24 - [Svelte Interactive Roles on Structural Elements]
**Learning:** Svelte's accessibility compiler enforces strict native HTML ARIA constraints (`a11y_no_noninteractive_element_to_interactive_role`). Applying `role="tablist"` to a semantic non-interactive element like `<nav>` violates this constraint.
**Action:** When implementing interactive ARIA patterns (like tabs) in Svelte, use structurally neutral elements (like `<div>` with descriptive classes) instead of semantic tags, and ensure the corresponding target containers (like `role="tabpanel"`) are given `tabindex="0"` for keyboard focusability.

## 2024-05-25 - [Dynamic Context for List Item Actions]
**Learning:** For repetitive list items with action buttons (like delete buttons), using static ARIA labels (e.g., `aria-label="Remove boundary condition"`) fails to provide screen reader users context about *which* item they are about to delete. Additionally, list elements that are dynamically updated need an `aria-live` region.
**Action:** Always use dynamic, contextual ARIA labels (e.g., `aria-label="Remove boundary condition for {bc.face_name}"`) by interpolating item data. Also, wrap the dynamic list and its empty state in a `<div aria-live="polite">` so additions/removals are announced.

## 2024-05-26 - [Playwright Interaction with Native Dialogs]
**Learning:** When implementing UX improvements that utilize native browser dialogs (such as `window.confirm` for destructive actions), automated testing environments like Playwright will hang because they do not automatically accept or dismiss these dialogs, leading to test timeouts and failures.
**Action:** Always update the corresponding Playwright tests by explicitly handling the dialog event using `page.once('dialog', dialog => dialog.accept())` or `.dismiss()` immediately before triggering the action that spawns the dialog. This ensures the automated test suite continues to function correctly and accurately tests both confirmation states.

## 2024-05-26 - [HTML5 Validation in Engineering Inputs]
**Learning:** In physics/engineering applications, unbounded number inputs can allow users to enter physically impossible values (e.g., negative density or negative time steps), which can lead to simulation failures or invalid data generation later in the pipeline.
**Action:** Always pair `type="number"` inputs with explicit `min` and/or `max` attributes (e.g., `min="0"`) for physical parameters. This utilizes the native browser HTML5 form validation to provide immediate, accessible UX boundaries without requiring complex custom validation logic.

## 2024-05-27 - [Detailed API Error Feedback & Input Reset]
**Learning:** Returning generic "Failed" messages from the frontend hides valuable API-level constraints (like "File size exceeds 50MB"). Additionally, if an `<input type="file">` is not cleared after an error, the user cannot easily select the *same* file to try again, leading to broken retry interactions.
**Action:** When handling form or file submission errors, attempt to extract and display the specific API error detail instead of a generic fallback. Furthermore, always reset the `<input>` value in the catch block so the user can seamlessly retry their action.

## 2024-06-25 - [Preventing Duplicate State Interactions in Form Selects]
**Learning:** When users populate lists from a `<select>` dropdown (like adding Boundary Conditions for faces), leaving already-used options selectable can lead to duplicate, erroneous entries that break downstream processing. Additionally, failing to reset the select input after an action leaves the UI in a confusing state.
**Action:** Conditionally apply the `disabled` attribute to `<option>` tags whose corresponding values already exist in the active collection, and append contextual text (like "(Already Added)"). Additionally, explicitly reset the bound variable (e.g., `selectedFace = ""`) upon successful insertion to prompt a fresh selection cycle.

## 2024-07-28 - [Accessible Fallbacks for Async Svelte Components]
**Learning:** When using Svelte's `{#await}` blocks to lazy-load heavy components (like 3D viewers), the dynamically rendered `{:catch}` error states and initial loading fallbacks are not automatically announced by screen readers since they are inserted asynchronously into the DOM.
**Action:** Always pair visual loading indicators in async component fallbacks with an explicit ARIA live region (e.g., `role="status" aria-live="polite"` for loading, and `role="alert" aria-live="assertive"` for errors) to ensure assistive technologies announce the state transition.
## 2024-04-13 - [Semantic Forms for Keyboard UX]
**Learning:** Standard HTML `<div>` wrappers and `<button on:click={handler}>` implementations for cohesive data entry sets completely break native implicit form submission (pressing the "Enter" key).
**Action:** Replace cohesive input `<div>` clusters with semantic `<form on:submit|preventDefault={handler}>` tags, and ensure the primary action uses a `<button type="submit">`. This instantly restores Enter-to-submit functionality natively without needing custom keydown event listeners, significantly improving both accessibility and power-user workflow speeds.

## 2024-08-15 - [Contextualizing Empty States and Disabled Buttons]
**Learning:** Using `placeholder` text within a `<textarea>` for an empty state is often insufficiently accessible and visually rigid. Furthermore, disabling a primary action button (like "Generate") without explaining *why* it is disabled leaves users confused about the system state.
**Action:** Replace `placeholder` text on empty textareas with explicitly styled, absolute-positioned empty state overlays containing clear instructions. Additionally, when disabling buttons based on state (like caching), update the button text to reflect the state (e.g., "Up to Date") and provide a `title` attribute explaining the condition to sighted users.
## 2024-11-20 - [Keyboard Accessibility for Tabbed Interfaces]
**Learning:** Native tablist navigation requires keyboard navigation (Left/Right arrows) to cycle through tabs, but standard HTML buttons only receive `Tab` focus sequentially. This creates a disjointed experience for keyboard-only or screen reader users trying to quickly switch between related configuration panels.
**Action:** When implementing custom `role="tablist"` elements in Svelte, always bind a `keydown` handler on the tab buttons to explicitly manage `tabindex` and focus state, allowing arrow keys to fluidly switch the active tab and focus.

## 2024-11-21 - [Extended Keyboard Support for Tab Navigation]
**Learning:** Adding support for `Home` and `End` keys in tabbed navigation implementations provides essential quick-navigation options, ensuring full alignment with the W3C WAI-ARIA Authoring Practices for tablists and improving accessibility for keyboard users who rely on shortcuts.
**Action:** Always implement `Home` (jump to first) and `End` (jump to last) key handlers alongside standard directional arrows (`ArrowLeft` / `ArrowRight`) when building custom ARIA `tablist` components to maximize navigation efficiency and standards compliance.

## 2024-11-22 - [Proper ARIA Structure for CSS-Toggled Tabs]
**Learning:** When using CSS display toggling for tab panels (to preserve state and avoid expensive unmounting), wrapping multiple disconnected sections in a single `role="tabpanel"` breaks screen reader expectations. Assistive technologies expect a 1:1 mapping between a `role="tab"` and its corresponding `role="tabpanel"`.
**Action:** Always wrap each individual tab section in its own `role="tabpanel"`, assign it a unique `id`, use `aria-labelledby` referencing the tab button, and conditionally apply `tabindex="0"` only to the active panel (and `-1` to inactive panels) so they are individually focusable and correctly announced.

## 2024-11-23 - [Visual Required Indicators on Form Fields]
**Learning:** While `required` attributes are essential for native browser validation and screen reader announcement, relying solely on them without a visual indicator (like an asterisk) creates an ambiguous UX for sighted users who don't know a field is required until they attempt to submit and trigger an error. Also, when inserting inline elements like `<span>` into CSS flexbox column layouts (like `<label>` tags), text nodes need to be explicitly wrapped in their own `<span>` to prevent them from becoming separate flex items and breaking the layout.
**Action:** Always pair `required` HTML attributes with a visual indicator (e.g., `<span aria-hidden="true" title="Required">*</span>`). Ensure any text nodes sharing a flex container with the new indicator are wrapped together in a `<span>` to preserve existing `flex-direction` constraints.

## 2024-11-24 - [Visual Loading Overlays with aria-hidden]
**Learning:** When adding prominent visual loading overlays (like spinners or semi-transparent blockers) to a component that already has an existing `aria-live` region managing its loading state (e.g., in a header), assistive technologies will read the overlay text redundantly if it's not hidden. This spams screen readers while providing a good visual UX.
**Action:** Always apply `aria-hidden="true"` to new visual loading overlays when the loading state is already being announced by a dedicated `aria-live` region elsewhere in the component tree.

## 2024-11-25 - [Preventing Copy of Stale Data]
**Learning:** When displaying derived data (like a generated XML preview) alongside a primary "Copy" action button, leaving the copy button enabled while the derived data is in an "outdated/stale" state can lead users to accidentally copy and use invalid, stale configurations.
**Action:** Always conditionally disable secondary action buttons (like "Copy") that depend on synchronized state when that state becomes stale. Furthermore, when disabling these buttons, always provide a dynamic `title` and `aria-label` explaining *why* they are disabled (e.g., "Settings have changed. Generate XML first to copy.") to avoid confusing users.

## 2026-05-13 - [Preventing Unintended Navigation on File Drop]
**Learning:** In SPAs with custom drag-and-drop zones (like file uploaders), if a user accidentally drops a file outside the designated area, the browser's default behavior is to navigate away from the app and open the file. This results in an immediate, complete loss of application state and a very frustrating UX.
**Action:** Always intercept and prevent default `dragover` and `drop` events at the highest possible level (e.g., using `<svelte:window on:dragover|preventDefault on:drop|preventDefault />` in Svelte) to ensure stray file drops do not break the single-page application experience.

## 2024-11-26 - [Redundant aria-label on Implicitly Labeled Form Fields]
**Learning:** Adding `aria-label` or `title` attributes directly to `<select>` or `<input>` elements that are already properly wrapped inside a native `<label>` tag (implicit labeling) is an accessibility anti-pattern. Screen readers prioritize `aria-label` over the visible label's text content. This causes critical contextual information inside the `<label>`—such as required field indicators (e.g., "*") or dynamic subtext—to be skipped during announcement, resulting in a degraded experience for assistive technology users.
**Action:** When a form field is explicitly or implicitly labeled by a `<label>` element, do not add redundant `aria-label` or `title` attributes to the input itself. Let the native association handle the announcement so all visible textual context within the label is properly read to the user.

## 2024-11-27 - [Visible Placeholders by Avoiding Arbitrary Zero Defaults]
**Learning:** Pre-filling numeric inputs with arbitrary zero defaults (e.g., `let value = 0.0;`) forces users to manually select and delete the value before typing, and permanently hides helpful `placeholder` text (like `e.g. 10.5`).
**Action:** When a numeric input has no logical default value (like an arbitrary boundary condition magnitude), initialize its bound variable to `""` or `null` instead of `0` to ensure the placeholder is visible and reduce unnecessary keystrokes. Rely on native HTML5 validation (`required`) to enforce data entry.

## 2024-11-28 - [Detailed API Error Feedback via Response OK check]
**Learning:** When using `fetch()` in frontend code to make API calls, a 400 or 500 backend error does not throw an exception in the `try/catch` block.
**Action:** To prevent silent failures and provide actionable feedback, always explicitly check `!response.ok`, extract the specific error detail from the JSON response, and surface it in the UI instead of a generic fallback message.

## 2024-11-29 - [Focus Management and Asynchronous DOM Updates in Svelte]
**Learning:** When navigating between components or tabs, computing state changes (like `activeTab = newKey`) and immediately calling `.focus()` on a dynamically-bound element often fails in Svelte because the DOM updates asynchronously. If the element's focusability (e.g., `tabindex="0"`) depends on the new state, a synchronous `.focus()` call executes *before* the DOM reflects the state, breaking the keyboard navigation experience.
**Action:** Always insert `await tick();` (imported from `svelte`) between updating component state and attempting to shift focus to an element that depends on that state change. This ensures the browser's focus is correctly shifted only after the DOM has been fully rendered.

## 2024-11-30 - [Handling FastAPI Validation Arrays in Error Messages]
**Learning:** When surfacing API errors from a FastAPI backend using `errData.detail`, validation errors (HTTP 422) return `detail` as an array of objects, not a string. Passing this array directly to `new Error()` or injecting it into the UI casts it to `[object Object]`, hiding the actionable error text from the user and causing confusion.
**Action:** Always check if `errData.detail` is an array. If so, map over the array to extract the `.msg` (and optionally `.loc`) fields and join them into a readable string before throwing the error to ensure users receive clear, actionable feedback.

## 2024-12-01 - [Preventing Jarring State Changes on Absolute Overlays]
**Learning:** When displaying loading states, empty states, or error overlays that are absolutely positioned over existing content (like a viewer canvas or textarea), relying solely on `#if` blocks without transitions causes them to instantly pop in and out. This creates a visually jarring UX, especially for brief loading operations, and violates the principle that state changes should feel smooth and continuous.
**Action:** Always apply a CSS transition or framework-provided animation (like Svelte's `transition:fade|local={{ duration: 150 }}`) to conditionally rendered, absolute-positioned overlay elements. This ensures they crossfade smoothly over the underlying content, significantly improving visual polish and perceived performance.

## 2024-12-02 - [Spatial Keyboard Navigation for Grid Tablists]
**Learning:** When a `role="tablist"` is laid out visually as a 2D grid (e.g., 2x2) rather than a simple 1D row or column, relying solely on standard linear navigation (`ArrowLeft` / `ArrowRight`) creates a disconnect between the visual layout and keyboard interaction. Users naturally expect `ArrowDown` to move focus to the item physically below the current one.
**Action:** When creating a multi-row or grid-based tablist, always extend standard tab keyboard navigation to support spatial navigation (`ArrowUp` and `ArrowDown`) by calculating the appropriate visual index offsets based on the grid structure, matching the user's mental model and expectations.
## 2024-12-03 - [Auto-Select Text on Numeric Input Focus]
**Learning:** When numeric input fields contain pre-filled data or represent dense configurations (like physical parameters), forcing users to manually highlight or repeatedly press backspace to clear the value before typing new data creates unnecessary friction.
**Action:** Always implement an auto-select on focus behavior (e.g., `on:focus={(e) => e.target.select()}` in Svelte) for input fields that typically require complete replacement rather than appending, significantly reducing keystrokes and improving data entry efficiency.
