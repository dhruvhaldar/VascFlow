## 2024-06-15 - Global Keyboard Shortcut for Viewer Camera Reset
**Learning:** For frequent primary actions like resetting a 3D view, users benefit greatly from global keyboard shortcuts. However, it is crucial to properly gate these global shortcuts by checking `event.target.tagName` to avoid accidentally triggering them while the user is typing inside `<input>` or `<textarea>` fields.
**Action:** When implementing global `<svelte:window on:keydown>` shortcuts, always include a check `if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") return;` to prevent interference with standard form entry.
## 2024-06-17 - Prevent Number Input Scroll Hijacking and Remove Spin Buttons
**Learning:** Native `<input type="number">` fields used for dense numerical configurations (e.g. physics simulations) suffer from two significant UX issues: accidental value mutation via scroll-wheel (often when users are just trying to scroll the page) and visual clutter from native spin arrows, which are rarely useful for precise decimal inputs.
**Action:** When using number inputs for precise numerical data, always append `on:wheel={(e) => e.currentTarget.blur()}` to prevent scroll hijacking, and apply CSS (`::-webkit-inner-spin-button`, `-moz-appearance: textfield`) to hide the default spin arrows for a cleaner layout.
## 2024-05-20 - Explicit Inline Validation for Empty States
**Learning:** When inputs begin empty and are required, users with assistive tech or who tab through fields without completing them might not realize a field is invalid until form submission. We rely on the native HTML5 constraint validation (`:invalid` pseudo-class), but we also need to inform screen reader users via `aria-invalid` since the browser doesn't automatically expose CSS pseudo-classes as ARIA states.
**Action:** Always add dynamic `aria-invalid` boolean logic directly matching the "empty/unselected" state for required dropdowns and text/number inputs to ensure the CSS `:invalid` feedback is parity-matched in the accessibility tree.
## 2024-06-19 - Accessible Inline Form Validation
**Learning:** Relying solely on HTML5 native validation and CSS `:invalid` pseudo-classes is insufficient for accessibility. While sighted users see a red border, screen reader users might not know the exact reason a form field is invalid unless explicit text is provided.
**Action:** Always provide explicit, text-based inline error messages (e.g., `<span role="alert">`) and link them to the input field using `aria-describedby` to ensure screen readers announce the exact error reason when the field receives focus.

## 2026-06-20 - Expose background tab validation errors at the tab level
**Learning:** When validation errors happen inside background tabs, users are often unaware because the errors are hidden until the tab is clicked.
**Action:** Append contextual visual badges and `aria-label` additions to tab buttons to proactively communicate background validation errors to both sighted and screen reader users.
## 2024-06-25 - Avoid `aria-live` on Large Generated Textareas
**Learning:** Applying `aria-live="polite"` directly to a `<textarea>` element that contains large generated code blocks (such as XML configurations) is a massive accessibility antipattern. When the configuration updates, screen readers will attempt to read the *entire* multi-line content, overwhelming the user and degrading the UX.
**Action:** Never use `aria-live="polite"` directly on a `<textarea>` displaying generated code. Instead, remove the attribute and use a visually hidden live region (e.g., `<div class="sr-only" aria-live="polite">`) to announce succinct state transitions like 'Generating...' or 'Generation complete'.
## 2024-06-25 - Fix global keyboard shortcut interfering with select dropdowns
**Learning:** Global single-character keyboard shortcuts (like 'R' to reset a camera) can conflict with native browser behavior, such as type-to-select navigation within `<select>` dropdowns. When checking `event.target.tagName` to ignore form inputs, developers often forget to include `SELECT`.
**Action:** When gating global keyboard shortcuts, explicitly ignore `event.target.tagName === 'SELECT'` alongside `INPUT` and `TEXTAREA` to preserve native keyboard accessibility for dropdown menus.

## 2024-06-25 - Fix skip-link focus outline
**Learning:** Removing the focus outline from a skip link (`outline: none;`) makes it completely invisible to keyboard users who rely on focus rings to navigate the page, violating accessibility guidelines.
**Action:** Ensure skip links either inherit the global `:focus-visible` styles or provide a high-contrast focus ring (e.g., `outline: 2px solid #fff`) when they receive keyboard focus.
## 2024-06-25 - Hide Symbolic Keyboard Shortcuts from Screen Readers
**Learning:** When using `<kbd>` tags to display keyboard shortcuts that include symbolic characters (like ⌘ or ↵), screen readers may read them literally (e.g., "Command slash Control plus Enter arrow"), which is extremely confusing.
**Action:** Always add `aria-hidden="true"` to `<kbd>` tags that contain symbols or non-alphanumeric characters, and place a visually hidden `span` (`<span class="sr-only">`) immediately after it with a clear, readable text alternative (e.g., "Command or Control plus Enter").
## 2024-06-27 - Name drag and drop regions for accessibility
**Learning:** Elements used as interactive drag-and-drop zones (e.g., file upload areas) often function as major interaction points but lack semantic meaning if not properly labeled. Screen reader users navigating by landmarks will bypass them without context.
**Action:** Always assign a semantic role (like `role="region"`) and an accessible name (using `aria-labelledby` pointing to an inner heading) to custom drag-and-drop container elements to ensure they are discoverable via assistive technologies.

## 2024-07-01 - Style File Input Parent on Focus Within
**Learning:** When a native `<input type="file">` is placed inside a larger, custom drag-and-drop region, it can receive keyboard focus. If the parent container doesn't provide visual feedback for this focus state (similar to its hover or dragging state), keyboard users will have no clear indication that they are currently interacting with the upload zone.
**Action:** Always apply `:focus-within` styling to custom drag-and-drop containers that wrap native interactive elements (like file inputs) to ensure keyboard navigation parity with mouse interactions.

## 2024-07-02 - Expand Click Target for Drag-and-Drop Zones
**Learning:** When using a native `<input type="file">` inside a larger custom drag-and-drop region, users intuitively expect the entire region to be clickable. If only the native input responds to clicks, it creates frustrating "dead zones" where a user clicks but nothing happens, breaking the illusion of a unified component.
**Action:** Always make the entire drag-and-drop container clickable by binding an `on:click` handler that programmatically triggers the hidden file input (`input.click()`), and apply `cursor: pointer` along with hover states to the container to visually communicate its interactivity.

## 2024-07-03 - Provide Instant Frontend Feedback for Invalid File Extensions in Drag-and-Drop Zones
**Learning:** While the native HTML `<input type="file" accept="...">` attribute prevents users from selecting invalid files via the OS file picker dialog, it does not prevent users from dragging and dropping invalid files directly onto the drop zone. If client-side validation is missing, these invalid files are uploaded to the backend, causing a delayed, confusing API error.
**Action:** Always implement explicit, programmatic client-side file extension validation (e.g., checking `file.name.endsWith()`) within the `onDrop` handler of drag-and-drop zones. Surface a clear, instant error message explaining exactly which file types are supported, and return early to prevent unnecessary network requests.

## 2024-07-04 - Clamp vertical spatial navigation for tabs grid
**Learning:** When extending standard linear keyboard navigation to support spatial navigation (`ArrowUp` and `ArrowDown`) for 2D grids (like a multi-row tablist), wrapping vertical movement around using modulo arithmetic breaks the user's spatial mental model by jumping focus to unexpected ends of the grid.
**Action:** Always clamp vertical movement (using `Math.min` and `Math.max`) to the grid boundaries rather than using modulo wrapping.
