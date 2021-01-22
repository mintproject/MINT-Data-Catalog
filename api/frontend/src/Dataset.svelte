<script>
    import {datasetNameSearch} from './stores';
    import {dataCatalogRequest} from './utils.js';
    import NestedKeyVal from './NestedKeyVal.svelte';
    import KeyVal from './KeyVal.svelte';
    import EditableContent from './EditableContent.svelte';
    import DTrans from './DTrans.svelte';

    console.log("STORES " + $datasetNameSearch);

    let pathArray = window.location.pathname.split('/');

    function is_mint_understandable(ds) {
        return ds.metadata !== undefined && ds.metadata.hasOwnProperty("resource_repr");
    }

    function isGuid(str) {
        str = str.replace("'", "").replace('"', '');
        var regexGuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return regexGuid.test(str);
    }

    const reserved_dataset_metadata_keys = new Set(['category_tags', 'license', 'description', 'version', 'source_url', 'limitations']);

    function stateManager() {

        const statuses = ['ready', 'editing', 'reviewing'];
        const displayNames = {
            'ready': undefined,
            'editing': ''
        };

        let statusIdx = 0;

        function nextState() {
            statusIdx = statusIdx === statuses.length - 1 ? 0 : statusIdx + 1
        }

        function previousState() {
            statusIdx = statusIdx === 0 ? statuses.length - 1 : statusIdx - 1
        }

        function currentState() {
            return statuses[statusIdx];
        }

        return Object.freeze({
            nextState,
            previousState,
            currentState
        })
    }

    const state = stateManager();

    let dataset;
    let dataset_id = pathArray[2];
    let datasetResults = {result: undefined, isError: false, error: undefined};
    let datasetVariableResults = {result: undefined, isError: false, error: undefined};
    let datasetResourcesResults = {result: undefined, isError: false, error: undefined};

    let datasetEdits = {};
    $: dataset = datasetResults['result'];
    $: {console.log(dataset)};
    $: variables = (datasetVariableResults['result'] !== undefined
        && datasetVariableResults['result']['dataset'] !== undefined
        && datasetVariableResults['result']['dataset']['variables']
    ) ? datasetVariableResults['result']['dataset']['variables'] : [];

    $: resources = (datasetResourcesResults['result'] !== undefined
        && datasetResourcesResults['result']['dataset'] !== undefined
        && datasetResourcesResults['result']['dataset']['resources']
    ) ? datasetResourcesResults['result']['dataset']['resources'] : [];

    $: isEdited = dataset !== undefined && Object.entries(datasetEdits).filter(([key, val]) => dataset[key] !== val && dataset.metadata[key] !== val).length > 0;

    let isEditing = false;

    let finishedFetchingDatasets = false;
    let finishedFetchingDatasetVariables = false;
    let finishedFetchingDatasetResources = false;
    let isError = false;

    const query = {
        "dataset_id": dataset_id
    };

    const datasetRequestor = dataCatalogRequest("http://localhost:7000/datasets/get_dataset_info", query);
    const datasetVariablesRequestor = dataCatalogRequest("http://localhost:7000/datasets/dataset_variables", query);
    const datasetResourcesRequestor = dataCatalogRequest("http://localhost:7000/datasets/dataset_resources", query);

    // const datasetRequestor = dataCatalogRequest("https://api.mint-data-catalog.org/datasets/get_dataset_info", query);
    // const datasetVariablesRequestor = dataCatalogRequest("https://api.mint-data-catalog.org/datasets/dataset_variables", query);
    // const datasetResourcesRequestor = dataCatalogRequest("https://api.mint-data-catalog.org/datasets/dataset_resources", query);


    function handleDatasetsResponse(responsePayload, reason) {
        finishedFetchingDatasets = true;
        if (responsePayload !== undefined) {
            datasetResults.result = responsePayload;
        } else {
            // doing assignment in a single call to avoid multiple Svelte invalidations and therefore refreshes
            datasetResults = Object.assign(datasetResults, {error: reason, isError: true});
        }
    }

    function handleDatasetVariablesResponse(responsePayload, reason) {
        finishedFetchingDatasetVariables = true;
        if (responsePayload !== undefined) {
            datasetVariableResults.result = responsePayload;
        } else {
            datasetVariableResults = Object.assign(datasetVariableResults, {error: reason, isError: true});
        }
    }

    function handleDatasetResourcesResponse(responsePayload, reason) {
        finishedFetchingDatasetResources = true;
        if (responsePayload !== undefined) {
            datasetResourcesResults.result = responsePayload;
        } else {
            datasetResourcesResults = Object.assign(datasetResourcesResults, {error: reason, isError: true});
        }
    }

    function startEditing() {
        isEditing = true;
    }

    function cancelEditing() {
        isEditing = false;
        datasetEdits = {};
        dataset = dataset;
    }



    datasetRequestor(handleDatasetsResponse);
    datasetVariablesRequestor(handleDatasetVariablesResponse);
    datasetResourcesRequestor(handleDatasetResourcesResponse);

    function handleClick() {
        window.location.href = '/';
    }

    const dataset_schema = {
        id: {
            type: "String",
            required: true,
            editable: false
        },
        name: {
            type: "String",
            required: true,
            editable: true
        },
        description: {
            type: "Text",
            required: false,
            editable: true,
            default: ""
        },
        created_at: {
            type: "DateTime",
            editable: false,
            required: true
        },
        metadata: {
            type: "Object",
            editable: true,
            required: false,
            default: {}
        }
    };

    function handleMessage(event) {
        const key = event.detail.key;
        const value = event.detail.value;

        if (datasetEdits[key] === undefined && dataset[key] !== value) {
            datasetEdits[key] = value;
        } else if (dataset[key] === value) {
            delete datasetEdits[key];
        }

        datasetEdits = datasetEdits;

        console.log(event);
        console.log(datasetEdits);
    }

    function saveChanges() {
        Object.entries(datasetEdits).forEach(([key, val]) => {
            if (dataset[key] !== undefined) {
                dataset[key] = val;
            } else {
                dataset.metadata[key] = val;
            }
        });

        datasetEdits = {};
        dataset = dataset;
        isEditing = false;
    }

</script>


<style>
    .dataset_summary {
        border-style: solid;
        border-color: #eee;
        border-width: 1px;
        border-radius: 5px;
        padding: 10px;
        margin-left: 10px;
        margin-right: 10px;
        margin-bottom: 30px;
        background-color: #fdfdfd;
        box-shadow: 2px 2px 3px 1px #eee;
    }

    .dataset_summary h4 {
        margin-bottom: 0px;
    }

    .dataset_summary p {
        margin-top: 2px;
    }

    .dataset_id {
        color: #bbb;
        font-size: 75%;
        padding-left: 0.5em;
    }

    .variable_id {
        color: #bbb;
        font-size: 75%;
    }

    .resource_id {
        color: #bbb;
        font-size: 75%;
    }

    .resource_summary, .variable_summary {
        padding-top: 10px;
        padding-bottom: 10px;
        margin-bottom: 30px;
        background-color: #fdfdfd;
    }

    h2 {
        margin-top: 50px;
    }

    ul {
        list-style-type: none;
        margin: 1px;
        padding: 0;
    }
    li {
        margin-top: 10px;
        margin-bottom: 5px;
    }

    dl {
        display: grid;
        grid-template-columns: max-content auto;
    }

    dt {
        grid-column-start: 1;
        font-size:85%;
        font-weight: lighter;
    }
    dd {
        grid-column-start: 2;
        font-size: 90%;
        color: #333333;
    }

    fieldset {
        border-width: 0.5px;
        border-color: #eee;
        border-radius: 2px;
    }
    fieldset legend {
        color: #9a9a9a;
        font-size: 90%;
    }
</style>

<button on:click={handleClick}>
    Back to search
</button>

<!--<button on:click={toggleEditing}>{isEditing && isEdited ? 'Save Changes' : 'Edit'}</button>-->

<!--{#if isEditing}-->
<!--    <button on:click={cancelEditing}>Cancel Editing</button>-->
<!--    {#if isEdited}-->
<!--        <button on:click={saveChanges}>Save Changes</button>-->
<!--    {/if}-->
<!--{:else}-->
<!--    <button on:click={startEditing}>Edit</button>-->
<!--{/if}-->

{#if finishedFetchingDatasets}
<section>
    {#if datasetResults.isError}
        <div style="background-color: #bf414b">
            {JSON.stringify(datasetResults, null, 2)}
        </div>
    {:else}
    <div class="dataset_summary">
        <div>
            <h1 style="margin-bottom:0"><EditableContent contentKey='name' contentValue={dataset.name} isEditable={isEditing} on:message={handleMessage}/></h1>
            <div><span class="dataset_id">id: {dataset.dataset_id}</span></div>
        </div>
        <hr>

        {#if (is_mint_understandable(dataset))}
            <DTrans dataset_id={dataset.dataset_id} />
            <hr>
        {/if}

        <div>
            <h4>Description</h4>
            <p><EditableContent contentKey='description' contentValue={dataset.description} isEditable={isEditing} on:message={handleMessage}/></p>
        </div>
        <div>
            <h4>Category Tags</h4>
            <p>{dataset.metadata && dataset.metadata['category_tags'] ? dataset.metadata['category_tags'] : 'N/A'}</p>
        </div>
        <div>
            <h4>Source URL</h4>
            <p>
                {#if dataset.metadata && dataset.metadata['source_url']}
                    <a href="{dataset.metadata['source_url']}" target="_blank">{dataset.metadata['source_url']}</a>
                {:else}
                'N/A'
                {/if}
            </p>
        </div>
        <div>
            <h4>Limitations</h4>
            <p>{dataset.metadata && dataset.metadata['limitations'] ? dataset.metadata['limitations'] : 'N/A'}</p>
        </div>
        <div>
            <h4>Version</h4>
            <p>{dataset.metadata && dataset.metadata['version'] ? dataset.metadata['version'] : 'N/A'}</p>
        </div>

        {#if dataset.metadata}
<!--        <h4>Additional Metadata</h4>-->
<!--        <ul>-->
<!--            {#each Object.entries(dataset.metadata) as metadata_arr}-->
<!--                {#if metadata_arr[1] !== undefined && metadata_arr[1] !== null && !Number.isNaN(metadata_arr[1]) && metadata_arr[1].constructor === Object}-->
<!--                    <NestedKeyVal key={metadata_arr[0]} vals={metadata_arr[1]}/>-->
<!--                {:else}-->
<!--                    <KeyVal key={metadata_arr[0]} val={metadata_arr[1]} />-->
<!--                {/if}-->

<!--            {/each}-->
<!--        </ul>-->

        <NestedKeyVal key={'Additional Metadata'} vals={dataset.metadata} />

<!--        <h4>Additional Metadata</h4>-->
<!--            <dl>-->
<!--                {#each Object.entries(dataset.metadata) as metadata}-->
<!--                {#if !reserved_dataset_metadata_keys.has(metadata[0]) && metadata[0] !== 'spatial_coverage'}-->
<!--                    <dt>{metadata[0]}:</dt>-->
<!--                    {#if (typeof metadata[1] === 'object')}-->
<!--                    <dd>{JSON.stringify(metadata[1])}</dd>-->
<!--                    {:else if (String(metadata[1]).substring(1, 10).includes("://"))}-->
<!--                    <dd><a href={metadata[1]}>{metadata[1]}</a></dd>-->
<!--                    {:else}-->
<!--                    <dd>{metadata[1]}</dd>-->
<!--                    {/if}-->
<!--                {/if}-->
<!--                {/each}-->
<!--            </dl>-->

        {/if}
    </div>
    {/if}
</section>
{/if}

{#if finishedFetchingDatasetVariables}
<section>
    <h2>Variables ({variables.length})</h2>
    <hr>
    {#if datasetVariableResults.isError}
    <div style="background-color: #bf414b">
        Something went wrong and variables could not be loaded. Please try again a little later.
<!--        {JSON.stringify(datasetVariableResults, null, 2)}-->
    </div>
    {:else}
        <ul>
            {#each variables as variable, i}

            <li class="variable_summary">
                <div><span class="variable_name">{variable.variable_name}</span></div>
                <div><span class="variable_id">id: {variable.variable_id}</span></div>
                <dl>
                    <dt>Standard Variable Name:</dt>
                    <dd>{variable.standard_variables[0].standard_variable_name}</dd>
                    <div><span class="variable_id">standard_variable_id: {variable.standard_variables[0].standard_variable_id}</span></div>
                    <dt>Standard Variable URI:</dt>
                    <dd><a href={variable.standard_variables[0].standard_variable_uri} target="_blank">{variable.standard_variables[0].standard_variable_uri}</a></dd>
                    <dt>Standard Variable Ontology:</dt>
                    <dd>{variable.standard_variables[0].standard_variable_ontology}</dd>

                    {#if variable.variable_metadata}
                        {#each Object.entries(variable.variable_metadata) as metadata}
                        <dt>{metadata[0]}:</dt>
                            {#if (typeof metadata[1] === 'object')}
                            <dd>{JSON.stringify(metadata[1])}</dd>
                            {:else if (String(metadata[1]).substring(1, 10).includes("://"))}
                            <dd><a href={metadata[1]}>{metadata[1]}</a></dd>
                            {:else}
                            <dd>{metadata[1]}</dd>
                            {/if}
                        {/each}
                    {/if}
                </dl>
            </li>
            {/each}
        </ul>
    {/if}
</section>
{/if}

{#if finishedFetchingDatasetResources}
<section>
    <h2>Resources ({resources.length === 200 ? '200+' : resources.length})</h2>
    <hr>
    {#if resources.length === 200}
    <p style="background-color: yellow">
        <strong>Note: this dataset has more than 200 resources and complete list cannot be displayed at this time</strong>
    </p>
    {/if}
    {#if datasetResourcesResults.isError}
    <div style="background-color: #bf414b">
        Something went wrong and resources could not be loaded. Please try again a little later.
    </div>
    {:else}
        <ul>
            {#each resources as resource, i}
            <li class="resource_summary">
                <div><span class="resource_name">{resource.resource_name}</span></div>
                <div><span class="resource_id">id: {resource.resource_id}</span></div>
                <dl>
                    <dt>File Type:</dt>
                    <dd>{resource.resource_type}</dd>
                    <dt>Data URL:</dt>
                    <dd><a href={resource.resource_data_url} target="_blank">{resource.resource_data_url}</a></dd>
                        {#if resource.resource_metadata}
                            {#each Object.entries(resource.resource_metadata) as metadata}
                                <dt>{metadata[0]}:</dt>
                                {#if (typeof metadata[1] === 'object')}
                                <dd>{JSON.stringify(metadata[1])}</dd>
                                {:else if (String(metadata[1]).substring(1, 10).includes("://"))}
                                <dd><a href={metadata[1]}>{metadata[1]}</a></dd>
                                {:else}
                                <dd>{metadata[1]}</dd>
                                {/if}
                            {/each}
                        {/if}
                </dl>
            </li>
            {/each}
        </ul>
    {/if}
</section>
{/if}

