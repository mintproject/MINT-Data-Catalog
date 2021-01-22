<script>
    import {datasetNameSearch, querySpatialCoverage, datasetSpatialCoverage, queryTemporalCoverage} from "./stores";
    import Map from './Map.svelte';
    import Timeline from './Timeline.svelte';
    import DatasetSummary from './DatasetSummary.svelte';

    $: searchDisabled = ($datasetNameSearch === '' && $querySpatialCoverage === {});
    let promise;
    let results = [];
    let searchPerformed = false;
    let isSearching = false;
    let datasetCoverageGeometry = {};

    let selectedDataset;
    let selectedDatasetIndex;

    let mapComponent;
    let timelineComponent;

    console.log(`datasetNameSearch: ${$datasetNameSearch}`);

    async function queryDataCatalog() {
        // const url = "https://api.mint-data-catalog.org/datasets/search_v2";
        const url = "http://localhost:7000/datasets/search_v2";
        const query = {
            "limit": 500
        };

        if ($datasetNameSearch !== '') {
            query["search_query"] = [$datasetNameSearch];
        }

        if (!(Object.keys($querySpatialCoverage).length === 0 && $querySpatialCoverage.constructor === Object)) {
            query["spatial_coverage"] = $querySpatialCoverage;
        }

        if (!(Object.keys($queryTemporalCoverage).length === 0
            && $queryTemporalCoverage.constructor === Object
            && $queryTemporalCoverage['start_time'] !== undefined
            && $queryTemporalCoverage['end_time'] !== undefined
        )) {
            query["temporal_coverage"] = $queryTemporalCoverage;
        }
        // Default options are marked with *
        const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json'
                // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrer: 'no-referrer', // no-referrer, *client
            body: JSON.stringify(query) // body data type must match "Content-Type" header
        });
        // return await response.json(); // parses JSON response into native JavaScript objects

        const payload = await response.json();
        results = await payload;
        isSearching = false;

        if (response.ok) {
            searchPerformed = true;
            // console.log(JSON.stringify(payload));
        } else {
            throw new Error(payload);
        }
    }

    function handleClick() {
        results = [];
        isSearching = true;
        selectedDataset = undefined;
        selectedDatasetIndex = undefined;
        timelineComponent.hideTemporalCoverage();
        mapComponent.hideGeoJSON();

        promise = queryDataCatalog();
    }

    function handleKeyDown(event) {
        const ENTER_keycode = 13;

        if (event.keyCode === ENTER_keycode) {
            const search_button = document.getElementById('search-button');
            search_button.classList.add("active");
            // results = [];
            // isSearching = true;
            // promise = queryDataCatalog();
        }

    }
    function handleKeyUp(event) {
        const ENTER_keycode = 13;

        if (event.keyCode === ENTER_keycode) {
            const search_button = document.getElementById('search-button');

            search_button.classList.remove("active");
            search_button.click();
        }
    }

    function selectDataset(datasetDefinition, index) {
        const spatial_coverage = datasetDefinition['dataset_spatial_coverage'] || {};
        const dataset_metadata = datasetDefinition['dataset_metadata'] || {};
        const temporal_coverage = dataset_metadata['temporal_coverage'] || {};

        if (index !== selectedDatasetIndex) {
            // clear existing geoJSON layer
            mapComponent.hideGeoJSON();
            mapComponent.displayGeoJSON(datasetDefinition['dataset_spatial_coverage'] || {});
            timelineComponent.displayTemporalCoverage(temporal_coverage['start_time'], temporal_coverage['end_time']);
            selectedDataset = Object.assign({}, datasetDefinition);
            // selectedDataset = selectedDataset;
            // console.log(JSON.stringify(selectedDataset))
            selectedDatasetIndex = index;
        }
    }

    function handleMouseLeave() {
        timelineComponent.hideTemporalCoverage();
        mapComponent.hideGeoJSON();
        selectedDataset = undefined;
    }

    function is_mint_understandable(ds) {
        return ds.dataset_metadata !== undefined && ds.dataset_metadata.hasOwnProperty("resource_repr");
    }
</script>
<style>


    .scrollable {
        height: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        box-sizing: border-box;
    }

    #search-button:active {
        background-color: rgb(117, 168, 63);
    }

    #search-button {
        background-color: rgb(4, 143, 216);
        color: #fefefe;
    }



    /*button#search-button.active, #search-button:focus {*/
    /*    background-color: rgb(117, 168, 63) !important;*/
    /*    border-color: #666;*/
    /*}*/

    /*#search-button .disabled {*/
    /*    background-color: inherit;*/
    /*}*/



    /*.map-overlay {*/
    /*    position: absolute;*/
    /*    bottom: 5px;*/
    /*    left: 5px;*/
    /*    z-index: 4;*/
    /*}*/
    .filter_old {
        padding-left: 5px;
        padding-right: 5px;
        margin-bottom: 10px;
        display: flex;
        justify-content: flex-start;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .filter {
        grid-area: right;
        padding-left: 20px;
    }

    .search_results {
        grid-area: left;
        /*width: 400px;*/
        height: 100vh;
        display: flex;
        flex-direction: column;
        /*float: left;*/
        box-sizing: border-box;
        overflow-y: auto;
        overflow-x: hidden;
    }

    .dataset_id {
        color: #bbb;
        font-size: 60%;
    }

    .dataset_preview {
        display: grid;
        grid-template-columns: 2em auto;
        grid-template-rows: auto;
        grid-template-areas:
                "dataset-preview-left dataset-preview-right";

        height: 100%;
        max-height: 100px;
        max-width: 285px;
        width: 99%;
        cursor: pointer;
        /*padding: 2px;*/
        margin-bottom: 5px;
        /*box-sizing: border-box;*/
        border-top-right-radius: 75px;
        border-bottom-right-radius: 75px;
    }

    .dataset_preview_left {
        grid-area: dataset-preview-left;
        align-content: center;
        justify-content: center;
        padding-left: 0.35em;
        padding-top: 0.35em;
    }

    .dataset_preview_right {
        padding-top: 1em;
        padding-bottom: 1em;
        padding-right: 2em;
        box-sizing: border-box;
        grid-area: dataset-preview-right;
    }

    .dataset_preview:hover {
        background-color: #f3f3f3;
    }

    .dataset_preview.selected {
        background-color: #efefef;
    }

    .display {
        display: grid;
        grid-template-columns: 300px auto;
        grid-template-rows: auto;
        grid-template-areas:
                "left right";
    }

    .icon {
        position: relative;
        left: -1.6em;
        top: 1em;
        float: left;
    }

</style>

<div class="display">
    {#if isSearching}
        <section>
            <h2>Searching...</h2>
        </section>

    {:else if (!isSearching && searchPerformed)}
    <section>
        <h2 style="margin-bottom:15px">Found {results.length} results</h2>
        <hr style="border: 0.5px solid #eee">
        <div class="search_results">
            {#if results.length > 0}
            {#each results as dataset, i}

            <div class="dataset_preview"
                 class:selected="{selectedDatasetIndex === undefined && i === 0 ? (() => { selectDataset(dataset, i); return true })() : i === selectedDatasetIndex}"
                 on:mousedown='{(e) => {e.preventDefault(); selectDataset(dataset, i)}}'
            >
                <span class="dataset_preview_left">
                    {#if is_mint_understandable(dataset)}
                        {'\u2B50'}
                    {/if}
                </span>

                <div class="dataset_preview_right">
                        <span class="dataset_name">
                            <strong>{dataset.dataset_name.length > 50 ? dataset.dataset_name.substring(0, 50) + '...' : dataset.dataset_name}</strong>
                        </span>
                    <div><span class="dataset_id">id: {dataset.dataset_id}</span></div>
                </div>
            </div>
            {/each}
            {/if}
        </div>
    </section>
    {/if}

    <div class="filter">
        <span>
        <input type="text" style="width:757px; outline: none; margin-left: 20px" bind:value={$datasetNameSearch} on:keyup={handleKeyUp} on:keydown={handleKeyDown}>
        <button id='search-button' disabled={searchDisabled} on:click={handleClick}>
        Search Datasets
        </button>
    </span>
        <span style="display: flex">
            <Map lat={10} lon={34} zoom={3.5} bind:this={mapComponent} />
            <Timeline bind:this={timelineComponent} />
        </span>

        <!--        <div class="map-overlay">-->
        <!--        </div>-->
        {#if (selectedDataset !== undefined)}
        <DatasetSummary dataset={selectedDataset} />
        {/if}
    </div>
</div>



