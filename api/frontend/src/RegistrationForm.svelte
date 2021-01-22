<script>
    let dataset;
    let dataset_definition = {
        dataset_id: '<uuid>',
        dataset_name: 'dataset name',
        dataset_description: 'blah blah blah',
        dataset_metadata: {
            top_level1: {
                second_level1: 1,
                second_level2: 2,
            },
            top_level2: "top_level2_value"
        }
    }
</script>

<form>
    <fieldset>
        <legend>Dataset Definition</legend>
<!--        {#each Object.keys(dataset_definition) as key}-->
        <p>
            <label for="dataset_name">Dataset Name</label>
            <input type="text" id="dataset_name" name="Dataset Name" value={dataset_definition.dataset_name}>
        </p>
        <p>
            <label for="dataset_description">Dataset Description</label>
            <input type="text" id="dataset_description" name="Dataset Description" value={dataset_definition.dataset_description}>
        </p>

        <fieldset>
            <legend>Optional Metadata</legend>
            <p>
                <label for="dataset_metadata.top_level1">dataset_metadata.top_level1</label>
                <input type="text" id="dataset_metadata.top_level1" name="Dataset Description" value={dataset_definition.dataset_description}>
            </p>
        </fieldset>

    </fieldset>

    <fieldset>
        <label for="variable_name">Variables</label>
        <input type="text" id="variable_name" name="Variable Name" value="variable_names">
    </fieldset>

    <fieldset>
        <legend>Resources</legend>
    </fieldset>
</form>
