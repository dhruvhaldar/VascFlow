<script>
    import { tick } from 'svelte';
    import { slide } from 'svelte/transition';
    import { simulationConfig, meshMetadata } from '../stores';

    let faceSelectElement;
    let selectedFace = "";
    let bcType = "Dirichlet";
    let variable = "Velocity";
    let value = "";
    let profile = "Flat";

    // ⚡ Bolt: Cache used face names in a reactive Set for O(1) lookups.
    // Calling array.some() twice per option inside an #each loop creates an
    // O(N*M) rendering bottleneck for meshes with many faces. Using a Set
    // reduces this to O(N+M), significantly improving UI responsiveness when
    // opening the dropdown or adding new boundary conditions.

    // ⚡ Bolt: Memoize the Set creation and DOM invalidation.
    // By splitting the reactive block, Svelte automatically skips updating usedFaceNames
    // if the boundary_conditions reference hasn't changed.
    $: bcs = $simulationConfig.boundary_conditions;
    $: usedFaceNames = new Set(bcs.map(bc => bc.face_name));

    async function addBC() {
        if (!selectedFace) return;
        simulationConfig.update(c => {
            const newBC = {
                face_name: selectedFace,
                bc_type: bcType,
                variable: variable,
                value: parseFloat(value),
                profile: profile,
                face_id: $meshMetadata.faces.find(f => f.name === selectedFace)?.id
            };
            c.boundary_conditions = [...c.boundary_conditions, newBC];
            return c;
        });
        selectedFace = "";

        // 🎨 Palette: Manage focus after adding BC.
        // Wait for DOM to update and then return focus to the Face select input,
        // so keyboard navigation can naturally continue.
        await tick();
        if (faceSelectElement) faceSelectElement.focus();
    }

    // ⚡ Bolt: Remove by unique ID instead of array index.
    // By passing faceName instead of the array index, we remove the
    // index dependency from the rendered DOM elements.
    async function removeBC(faceName) {
        if (window.confirm(`Are you sure you want to remove the boundary condition for ${faceName}?`)) {
            simulationConfig.update(c => {
                c.boundary_conditions = c.boundary_conditions.filter(bc => bc.face_name !== faceName);
                return c;
            });
            // 🎨 Palette: Manage focus after removing BC.
            // Wait for DOM to update and return focus to the Face select input,
            // to prevent focus dropping to <body> when the remove button disappears.
            await tick();
            if (faceSelectElement) faceSelectElement.focus();
        }
    }
</script>

<div class="bc-editor">
    <h3>Boundary Conditions</h3>

    {#if $meshMetadata.faces.length > 0}
        <form class="add-bc" on:submit|preventDefault={addBC}>
            <label>
                <span>Face<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:this={faceSelectElement} bind:value={selectedFace} required>
                    <option value="" disabled selected>Select Face</option>
                    <!-- ⚡ Bolt: Use a keyed each block for face options. -->
                    {#each $meshMetadata.faces as face (face.id)}
                        <option
                            value={face.name}
                            disabled={usedFaceNames.has(face.name)}
                        >
                            {face.name} (ID: {face.id}) {usedFaceNames.has(face.name) ? '(Already Added)' : ''}
                        </option>
                    {/each}
                </select>
            </label>

            <label>
                <span>Type<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:value={bcType} required>
                    <option value="Dirichlet">Dirichlet</option>
                    <option value="Neumann">Neumann</option>
                    <option value="Resistance">Resistance</option>
                </select>
            </label>

            <label>
                <span>Variable<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <input type="text" bind:value={variable} placeholder="Variable (e.g. Velocity)" required />
            </label>

            <label>
                <span>Value<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <input type="number" bind:value={value} step="any" placeholder="e.g. 10.5" required on:focus={(e) => e.target.select()} />
            </label>

            <label>
                <span>Profile<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:value={profile} required>
                    <option value="Flat">Flat</option>
                    <option value="Parabolic">Parabolic</option>
                </select>
            </label>

            <div class="submit-action">
                <button type="submit" disabled={!selectedFace} title={!selectedFace ? "Select a face first to add a boundary condition" : "Add boundary condition"}>Add BC</button>
            </div>
        </form>

        <div aria-live="polite">
            {#if $simulationConfig.boundary_conditions.length === 0}
                <p class="empty-state">No boundary conditions added yet. Select a face and configure parameters above to add one.</p>
            {:else}
                <ul>
                    <!-- ⚡ Bolt: Use a keyed each block based on face_name.
                         Combined with removing the index dependency in removeBC,
                         this guarantees O(1) DOM updates when removing an item,
                         rather than triggering an O(N) cascade update to re-bind
                         shifted array indices for all subsequent sibling elements. -->
                    {#each $simulationConfig.boundary_conditions as bc (bc.face_name)}
                        <li class="bc-item" transition:slide|local>
                            <span>{bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})</span>
                            <button class="remove-btn" on:click={() => removeBC(bc.face_name)} aria-label="Remove boundary condition for {bc.face_name}" title="Remove boundary condition for {bc.face_name}">&times;</button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    {:else}
        <p class="empty-state" role="alert">Please upload a mesh file first to detect faces and configure boundary conditions.</p>
    {/if}
</div>

<style>
    .bc-editor {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .add-bc {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        align-items: flex-end;
    }

    .add-bc label {
        display: flex;
        flex-direction: column;
        font-size: 0.85rem;
        color: #b8c5ef;
        gap: 0.25rem;
    }

    .add-bc input, .add-bc select {
        padding: 0.45rem 0.55rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 10px;
        background: rgba(12, 18, 40, 0.45);
        color: #f3f6ff;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }

    .add-bc input:hover:not(:disabled), .add-bc select:hover:not(:disabled) {
        border-color: rgba(255, 255, 255, 0.4);
        background: rgba(16, 24, 50, 0.6);
    }

    .add-bc input:invalid, .add-bc select:invalid {
        border-color: rgba(255, 77, 77, 0.5);
        background: rgba(255, 77, 77, 0.05);
    }

    .submit-action {
        display: flex;
        align-items: flex-end;
        padding-bottom: 0.1rem;
    }

    .submit-action button {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(80, 126, 246, 0.45);
        color: #f7f9ff;
        border-radius: 10px;
        padding: 0.45rem 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: inherit;
        font-size: 0.9rem;
    }

    .submit-action button:hover:not(:disabled) {
        background: rgba(80, 126, 246, 0.65);
        border-color: rgba(255, 255, 255, 0.35);
    }

    .required-indicator {
        color: #ffc2c2;
        margin-left: 0.2rem;
    }

    .empty-state {
        color: #b8c5ef;
        font-style: italic;
        margin-top: 1rem;
    }

    ul {
        padding-left: 1rem;
    }

    .bc-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.25rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .bc-item:last-child {
        border-bottom: none;
    }

    .remove-btn {
        background: transparent;
        border: 1px solid transparent;
        color: #ffc2c2;
        cursor: pointer;
        font-size: 1.2rem;
        line-height: 1;
        padding: 0.1rem 0.4rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    .remove-btn:hover {
        background: rgba(255, 77, 77, 0.15);
        color: #ff4d4d;
        border-color: rgba(255, 77, 77, 0.3);
    }

    .remove-btn:focus-visible {
        outline: 2px solid #ff4d4d;
        outline-offset: 2px;
    }
</style>
