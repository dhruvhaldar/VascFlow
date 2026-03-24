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
        border: 1px solid #ccc;
        padding: 1rem;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    textarea {
        flex: 1;
        width: 100%;
        font-family: monospace;
        resize: none;
        height: 300px;
    }
</style>
