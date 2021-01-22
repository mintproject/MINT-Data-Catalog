<script>
    import DTrans from './DTrans.svelte';

    export let dataset;

    function is_mint_understandable(ds) {
        return ds.dataset_metadata !== undefined && ds.dataset_metadata.hasOwnProperty("resource_repr");
    }
</script>

<style>
    .dataset_summary {
        /*border-style: solid;*/
        /*border-color: #eee;*/
        /*border-width: 1px;*/
        /*border-radius: 5px;*/
        padding: 10px;
        margin-left: 10px;
        margin-top: 20px;
        margin-right: 10px;
        margin-bottom: 30px;
        /*background-color: #fdfdfd;*/
        /*box-shadow: 2px 2px 3px 1px #eee;*/
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

    .dataset_summary .dataset_id {
        color: #bbb;
        font-size: 75%;
    }

    h4 {
        margin-bottom: 10px;
        color: #333;
    }

    .a-as-button {
        background-color: rgba(4, 143, 216, 0.8);
        color: #fff;
        border: none;
        padding: 5px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        /*font-size: 0.75em;*/
        margin: 20px 2px;
        border-radius: 5px;
        cursor: pointer;
        line-height: 1.5em;
    }

</style>


<section class="dataset_summary">
    <hr>
    {#if (is_mint_understandable(dataset))}
        <DTrans dataset_id={dataset.dataset_id} />
        <hr>
    {/if}
    <h4>Name</h4>
    <div style="padding-left: 20px">
        <span class="dataset_name">

            <strong>
                {dataset.dataset_name}
            </strong>

        </span>
        <div><span class="dataset_id">id: {dataset.dataset_id}</span></div>
    </div>

    <h4>Description</h4>
    <p style="padding-left: 20px">{dataset.dataset_description}</p>
    {#if dataset.dataset_metadata}
    <h4>Additional Metadata</h4>
    <div style="padding-left: 20px">
        <dl>
            {#each Object.entries(dataset.dataset_metadata) as metadata}
            <dt>{metadata[0]}:</dt>
                {#if (typeof metadata[1] === 'object')}
                <dd>{JSON.stringify(metadata[1])}</dd>
                {:else if (String(metadata[1]).substring(1, 10).includes("://"))}
                <dd><a href={metadata[1]}>{metadata[1]}</a></dd>
                {:else}
                <dd>{metadata[1]}</dd>
                {/if}
            {/each}
        </dl>
    </div>
    {/if}

    <hr>
    <button onclick="location.href='/datasets/{dataset.dataset_id}';" type="button">View more detailed information...</button>

<!--    <a href="/datasets/{dataset.dataset_id}" class="a-as-button">V.</a>-->
</section>
