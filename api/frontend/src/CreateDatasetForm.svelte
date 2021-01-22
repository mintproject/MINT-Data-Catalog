<script>
    const dataset = {};
    const reserved_dataset_metadata_keys = new Set(['category_tags', 'license', 'description', 'version', 'source_url', 'limitations']);
    let dataset_id, provenance_id, dataset_name, dataset_description, dataset_metadata;

    function register_dataset() {
        dataset['record_id'] = dataset_id;
        dataset['provenance_id'] = provenance_id;
        dataset['name'] = dataset_name;
        dataset['description'] = dataset_description;
        dataset['metadata'] = dataset_metadata;

        console.log(JSON.stringify(dataset_id));
    }
</script>

<form>
    <fieldset>
        <legend>Dataset Definition</legend>
        <!--        {#each Object.keys(dataset_definition) as key}-->

        <p>
            <label for="dataset_id">Dataset ID</label>
            <input type="text" id="dataset_id" name="Dataset ID" bind:value={dataset_id} required="true">
        </p>

        <p>
            <label for="provenance_id">Provenance ID</label>
            <input type="text" id="provenance_id" name="Provenance ID" bind:value={provenance_id}>
        </p>

        <p>
            <label for="dataset_name">Dataset Name</label>
            <input type="text" id="dataset_name" name="Dataset Name" bind:value={dataset_name}>
        </p>
        <p>
            <label for="dataset_description">Dataset Description</label>
            <input type="textarea" id="dataset_description" name="Dataset Description" bind:value={dataset_description}>
        </p>

        <fieldset>
            <legend>Optional Metadata</legend>
<!--            <p>-->
<!--                <label for="dataset_metadata.top_level1">dataset_metadata.top_level1</label>-->
<!--                <input type="text" id="dataset_metadata.top_level1" name="Dataset Description" value={dataset_definition.dataset_description}>-->
<!--            </p>-->

            <p>
                <label for="dataset_metadata">Dataset Metadata</label>
                <input type="text" id="dataset_metadata" name="Dataset Metadata" bind:value={dataset_metadata}>
            </p>
        </fieldset>

    </fieldset>

<!--    dataset_id: <input type="text" name="record_id" bind:value={dataset_id} required="true">-->
<!--    provenance_id: <input type="text" name="provenance_id" bind:value={provenance_id} required="true">-->
<!--    name: <input type="text" name="name" bind:value={dataset_name} required="true">-->
<!--    description <input type="textarea" name="dataset_description" bind:value={dataset_id}>-->
</form>

<button on:click={register_dataset}>
    Register
</button>