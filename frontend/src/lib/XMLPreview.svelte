<script>
    import { simulationConfig, generatedXML } from '../stores';

    let generating = false;

    async function generate() {
        generating = true;
        try {
            const response = await fetch("http://localhost:8000/generate_input", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify($simulationConfig)
            });
            const data = await response.json();
            generatedXML.set(data.xml);
        } catch (e) {
            console.error(e);
            generatedXML.set("Error generating XML");
        } finally {
            generating = false;
        }
    }
</script>

<div class="xml-preview">
    <div class="header">
        <h3>Input File Preview</h3>
        <button on:click={generate} disabled={generating} aria-busy={generating}>
            {generating ? 'Generating...' : 'Generate XML'}
        </button>
    </div>
    <textarea
        readonly
        value={$generatedXML}
        aria-label="Generated XML Preview"
        placeholder="Click 'Generate XML' to preview your input file."
    ></textarea>
</div>

<style>
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

    button {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(80, 126, 246, 0.45);
        color: #f7f9ff;
        border-radius: 10px;
        padding: 0.45rem 0.8rem;
        cursor: pointer;
    }

    textarea {
        flex: 1;
        width: 100%;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        resize: none;
        min-height: 220px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(8, 10, 24, 0.55);
        color: #ebf0ff;
        padding: 0.65rem;
    }
</style>
