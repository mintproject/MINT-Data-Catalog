<script>
    import { onMount } from 'svelte';

    onMount(() => {
        const redoc = document.createElement("redoc");
        const spec_url = document.createAttribute('spec-url');
        spec_url.value = '/api_doc.json';
        redoc.setAttributeNode(spec_url);


        const redoc_js = document.createElement("script");
        const redoc_js_src = document.createAttribute('src');
        redoc_js_src.value = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js";
        redoc_js.setAttributeNode(redoc_js_src);
        document.getElementById('documentation').appendChild(redoc);
        document.getElementById('documentation').appendChild(redoc_js);
    })
</script>
<style></style>
<!--<redoc spec-url='/api_doc.json'></redoc>-->
<div id="documentation">
</div>
