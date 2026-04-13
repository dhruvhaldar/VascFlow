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
