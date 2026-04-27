<script>
    import { simulationConfig, generatedXML } from '../stores';

    let generating = false;
    let copying = false;
    let copied = false;
    let lastConfigStr = null;

    $: currentConfigStr = JSON.stringify($simulationConfig);
    $: isUpToDate = $generatedXML && $generatedXML !== "Error generating XML" && currentConfigStr === lastConfigStr;

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
        }
    }

    async function generate() {
        // ⚡ Bolt: Cache generated XML to prevent redundant API calls.
        // If the simulation configuration hasn't changed since the last generation,
        // we skip the backend network request entirely. This saves network bandwidth
        // and eliminates API latency for repeated clicks.
        if (isUpToDate) {
            return;
        }

        generating = true;
        try {
            const response = await fetch("http://localhost:8000/generate_input", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: currentConfigStr
            });
            const data = await response.json();
            generatedXML.set(data.xml);
            lastConfigStr = currentConfigStr;
        } catch (e) {
            console.error(e);
            generatedXML.set("Error generating XML");
            lastConfigStr = null;
        } finally {
            generating = false;
        }
    }
</script>

<div class="xml-preview">
    <div class="header">
        <h3>Input File Preview</h3>
        <div class="actions">
            {#if $generatedXML && $generatedXML !== "Error generating XML"}
                <button
                    on:click={copyXML}
                    disabled={copying}
                    aria-label={copied ? "Copied to clipboard" : "Copy generated XML to clipboard"}
                    aria-live="polite"
                    class="secondary-button"
                    class:success={copied}
                >
                    {copied ? 'Copied!' : 'Copy XML'}
                </button>
            {/if}
            <button
                on:click={generate}
                disabled={generating || isUpToDate}
                aria-busy={generating}
                title={isUpToDate ? "XML is up to date with current settings" : "Generate XML"}
            >
                {generating ? 'Generating...' : (isUpToDate ? 'Up to Date' : 'Generate XML')}
            </button>
        </div>
    </div>
    <div class="preview-container">
        {#if !$generatedXML}
            <div class="empty-state">
                <p>No XML generated yet.</p>
                <p class="subtext">Configure your simulation and click 'Generate XML'.</p>
            </div>
        {:else if !isUpToDate}
            <div class="empty-state stale-overlay">
                <p>⚠️ Outdated Preview</p>
                <p class="subtext">Settings have changed. Click 'Generate XML' to update.</p>
            </div>
        {/if}
        <textarea
            readonly
            class:stale={$generatedXML && !isUpToDate}
            value={$generatedXML}
            aria-label="Generated XML Preview"
            aria-live="polite"
            tabindex={!$generatedXML || !isUpToDate ? -1 : 0}
            aria-hidden={!$generatedXML || !isUpToDate ? "true" : "false"}
        ></textarea>
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

    .empty-state .subtext {
        font-size: 0.85rem;
        opacity: 0.8;
    }
</style>
