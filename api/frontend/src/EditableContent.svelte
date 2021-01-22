<script>
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    export let isEditable = false;
    export let contentKey;
    export let contentValue;
    export let fieldType;

    let contentArea = 'contentArea';
    let currentContentValue = contentValue;


    let isEditing = false;
    let isEdited = false;
    $: isEdited = contentValue !== undefined && contentValue !== currentContentValue;

    function toggleEditing() {
        isEditing = !isEditing;
    }

    function undoChanges() {
        currentContentValue = contentValue;
    }

    function dispatchChanges() {
        dispatch('message', {key: contentKey, value: currentContentValue})
    }
</script>

<style>
    span {
        /*background: url(tutorial/icons/folder.svg) 0 0.1em no-repeat;*/
        /*background-size: 1em 1em;*/
        font-weight: bold;

        /*cursor: pointer;*/
    }

    [contenteditable="true"] {
        border-bottom: 1px dashed #464647;
    }

    /*.isEdited {*/
    /*    !*background-color: lightgoldenrodyellow;*!*/
    /*}*/

    .contentArea {
        padding: 0 0 0 0.2em;
        border-left: 0.25em solid transparent;
    }

    .contentArea.isEdited {
        border-left: 0.25em solid orange;
    }

    .expanded {
        /*background-image: url(tutorial/icons/folder-open.svg);*/
    }

    /*ul {*/
    /*    padding: 0.2em 0 0 0.5em;*/
    /*    margin: 0 0 0 0.5em;*/
    /*    list-style: none;*/
    /*    border-left: 1px solid #aaa;*/
    /*}*/

    /*li {*/
    /*    padding: 0.2em 0;*/
    /*}*/
</style>


<div class="contentArea {isEdited ? 'isEdited' : ''}">
    {#if isEditable}
        <span contenteditable='true' bind:textContent={currentContentValue} on:input={dispatchChanges}/>
<!--        <button on:click={undoChanges}/>-->
    {:else}
        <span class:isEdited={isEdited}>{currentContentValue}</span>
    {/if}
<!--    <button on:click={toggleEditing}></button>-->
</div>