<script>
    import { tick } from 'svelte';
    import { fade } from 'svelte/transition';
    import { simulationConfig, generatedXML } from '../stores';

    let generating = false;
    let copying = false;
    let copied = false;
    let downloaded = false;
    let lastConfigStr = null;
    let generateBtn;
    let copyBtn;

    $: currentConfigStr = JSON.stringify($simulationConfig);
    $: isError = $generatedXML === "Error generating XML";
    $: isUpToDate = $generatedXML && !isError && currentConfigStr === lastConfigStr;

    function downloadXML() {
        if (!$generatedXML) return;
        const blob = new Blob([$generatedXML], { type: "application/xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "svfsi.xml";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        downloaded = true;
        setTimeout(() => {
            downloaded = false;
        }, 2000);
    }

    async function copyXML() {
        if (!$generatedXML) return;
        copying = true;
        try {
            await navigator.clipboard.writeText($generatedXML);
            copied = true;
            setTimeout(() => {
                copied = false;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        } finally {
            copying = false;
            await tick();
            if (copyBtn) copyBtn.focus();
        }
    }

    let errorDetail = "";

    async function generate() {
        // ⚡ Bolt: Cache generated XML to prevent redundant API calls.
        // If the simulation configuration hasn't changed since the last generation,
        // we skip the backend network request entirely. This saves network bandwidth
        // and eliminates API latency for repeated clicks.
        if (isUpToDate) {
            return;
        }

        generating = true;
        errorDetail = "";
        try {
            const response = await fetch("http://localhost:8000/generate_input", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: currentConfigStr,
                signal: AbortSignal.timeout(10000)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                let errMsg = "Failed to generate XML";
                if (errData.detail) {
                    errMsg = Array.isArray(errData.detail)
                        ? errData.detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] + ': ' : ''}${d.msg}`).join(", ")
                        : errData.detail;
                }
                throw new Error(errMsg);
            }

            const data = await response.json();
            generatedXML.set(data.xml);
            lastConfigStr = currentConfigStr;
        } catch (e) {
            console.error(e);
            if (e.name === 'TimeoutError') {
                errorDetail = "Generation timed out. The server took too long to respond.";
            } else {
                errorDetail = e.message;
            }
            generatedXML.set("Error generating XML");
            lastConfigStr = null;
        } finally {
            generating = false;
            await tick();
            if (isUpToDate && copyBtn) {
                copyBtn.focus();
            } else if (generateBtn) {
                generateBtn.focus();
            }
        }
    }

    function handleGlobalKeydown(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            if (!generating && !isUpToDate) {
                generate();
            }
        }
    }
</script>

<svelte:window on:keydown={handleGlobalKeydown} />

<div class="xml-preview">
    <div class="header">
        <h3>Input File Preview</h3>
        <div class="actions">
            {#if $generatedXML && !isError}
                <button
                    on:click={downloadXML}
                    disabled={!isUpToDate}
                    aria-label={!isUpToDate ? "Generate XML to download updated settings" : (downloaded ? "Downloaded XML file" : "Download generated XML file")}
                    title={!isUpToDate ? "Settings have changed. Generate XML first to download." : "Download XML"}
                    aria-live="polite"
                    class="secondary-button"
                    class:success={downloaded}
                >
                    {downloaded ? 'Downloaded!' : 'Download'}
                </button>
                <button
                    bind:this={copyBtn}
                    on:click={copyXML}
                    disabled={copying || !isUpToDate}
                    aria-label={!isUpToDate ? "Generate XML to copy updated settings" : (copied ? "Copied to clipboard" : "Copy generated XML to clipboard")}
                    title={!isUpToDate ? "Settings have changed. Generate XML first to copy." : "Copy XML"}
                    aria-live="polite"
                    class="secondary-button"
                    class:success={copied}
                >
                    {copied ? 'Copied!' : 'Copy'}
                </button>
            {/if}
            <button
                bind:this={generateBtn}
                on:click={generate}
                disabled={generating || isUpToDate}
                aria-busy={generating}
                title={isUpToDate ? "XML is up to date with current settings" : "Generate XML (Ctrl/Cmd + Enter)"}
                aria-keyshortcuts="Control+Enter Meta+Enter"
                class="generate-btn"
            >
                {#if generating}
                    <span class="inline-spinner" aria-hidden="true"></span>
                {/if}
                {#if generating}
                    Generating...
                {:else if isUpToDate}
                    Up to Date
                {:else}
                    Generate XML <kbd class="shortcut-hint" aria-hidden="true">⌘/Ctrl+↵</kbd>
                {/if}
            </button>
        </div>
    </div>
    <div class="preview-container">
        {#if !$generatedXML}
            <div class="empty-state" transition:fade|local={{ duration: 150 }}>
                <p>No XML generated yet.</p>
                <p class="subtext">Configure your simulation and click 'Generate XML' (or press <kbd class="shortcut-hint">⌘/Ctrl+↵</kbd>).</p>
            </div>
        {:else if isError}
            <div class="empty-state error-state" role="alert" aria-live="assertive" transition:fade|local={{ duration: 150 }}>
                <p>❌ Failed to generate XML</p>
                <p class="subtext">{errorDetail || "Please check your simulation settings (ensure density/viscosity are valid) and try again."}</p>
            </div>
        {:else if !isUpToDate}
            <div class="empty-state stale-overlay" transition:fade|local={{ duration: 150 }}>
                {#if generating}
                    <span class="inline-spinner" style="width: 24px; height: 24px; margin-bottom: 0.5rem;" aria-hidden="true"></span>
                    <p>Generating updated XML...</p>
                {:else}
                    <p>⚠️ Outdated Preview</p>
                    <p class="subtext">Settings have changed. Click 'Generate XML' (or press <kbd class="shortcut-hint">⌘/Ctrl+↵</kbd>) to update.</p>
                {/if}
            </div>
        {/if}

        {#if !isError}
            <textarea
                readonly
                class:stale={$generatedXML && !isUpToDate}
                value={$generatedXML}
                aria-label="Generated XML Preview"
                aria-live="polite"
                tabindex={!$generatedXML || !isUpToDate ? -1 : 0}
                aria-hidden={!$generatedXML || !isUpToDate ? "true" : "false"}
                on:focus={(e) => e.target.select()}
                on:click={(e) => e.target.select()}
            ></textarea>
        {/if}
    </div>
</div>

<style>
    textarea.stale {
        opacity: 0.4;
        pointer-events: none;
    }

    .stale-overlay {
        z-index: 5;
        background: rgba(8, 10, 24, 0.75);
        border-radius: 10px;
    }

    .stale-overlay p:first-child {
        color: #ffda85;
    }

    .xml-preview {
        display: flex;
        flex-direction: column;
        height: 100%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    button {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(80, 126, 246, 0.45);
        color: #f7f9ff;
        border-radius: 10px;
        padding: 0.45rem 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    button:hover:not(:disabled) {
        background: rgba(80, 126, 246, 0.65);
        border-color: rgba(255, 255, 255, 0.35);
    }

    button.secondary-button {
        background: rgba(255, 255, 255, 0.1);
    }

    button.secondary-button:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.2);
    }

    button.success {
        background: rgba(76, 175, 80, 0.35);
        border-color: rgba(76, 175, 80, 0.5);
    }

    .preview-container {
        flex: 1;
        position: relative;
        display: flex;
        min-height: 220px;
    }

    textarea {
        flex: 1;
        width: 100%;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        resize: none;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(8, 10, 24, 0.55);
        color: #ebf0ff;
        padding: 0.65rem;
    }

    .empty-state {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #b8c5ef;
        text-align: center;
        pointer-events: none;
    }

    .empty-state p {
        margin: 0.25rem 0;
    }

    .error-state {
        z-index: 5;
        background: rgba(255, 77, 77, 0.1);
        border: 1px solid rgba(255, 77, 77, 0.3);
        border-radius: 10px;
    }

    .error-state p:first-child {
        color: #ffc2c2;
        font-weight: 600;
    }

    .empty-state .subtext {
        font-size: 0.85rem;
        opacity: 0.8;
    }

    .generate-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }

    .inline-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255, 255, 255, 0.25);
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .shortcut-hint {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.75rem;
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #b8c5ef;
        margin-left: 0.2rem;
    }
</style>
