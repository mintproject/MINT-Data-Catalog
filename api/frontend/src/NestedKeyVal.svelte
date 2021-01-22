<script>
    import KeyVal from './KeyVal.svelte';

    export let expanded = false;
    export let key;
    export let vals;

    function toggle() {
        expanded = !expanded;
    }
</script>

<style>
    span {
        padding: 0 0 0 0.25em;
        /*background: url(tutorial/icons/folder.svg) 0 0.1em no-repeat;*/
        /*background-size: 1em 1em;*/
        font-weight: bold;
        cursor: pointer;
    }

    .expanded {
        /*background-image: url(tutorial/icons/folder-open.svg);*/
    }

    ul {
        padding: 0.2em 0 0 0.5em;
        margin: 0 0 0 0.5em;
        list-style: none;
        border-left: 1px solid #aaa;
    }

    li {
        padding: 0.2em 0;
    }
</style>

<span class:expanded on:click={toggle}>{expanded ? '\u25BE' : '\u25B8'} {key}</span>

{#if expanded}
<ul>
    {#each Object.entries(vals) as childKeyVals}
    <li>
        {#if childKeyVals[1] !== undefined
            && childKeyVals[1] !== null
            && !Number.isNaN(childKeyVals[1])
            && (childKeyVals[1].constructor === Object || Array.isArray(childKeyVals[1]))
        }
        <svelte:self key={childKeyVals[0]} vals={childKeyVals[1]} />
        {:else}
        <KeyVal key={childKeyVals[0]} val={childKeyVals[1]} />
        {/if}
    </li>
    {/each}
</ul>
{/if}