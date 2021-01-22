<script>
    import { onMount } from 'svelte';
    import {queryTemporalCoverage} from './stores';

    let containerHeight = 300;
    let containerWidth = 200;

    let timeRangeEnd = 160;
    let timeLine = 50;

    let timeLinePadding = 40;
    let isModified = false;

    let highlightStart;
    let highlightEnd;

    let selectedElement;
    let dragStartY;
    let dragYOffset;
    let coordinateTransformMatrix;

    let leftRangeSlider;
    let rightRangeSlider;

    let minDate = new Date("1980-01-01T00:00:00");
    let maxDate = new Date();
    $: minYear = minDate.getUTCFullYear();
    $: maxYear = maxDate.getUTCFullYear();
    let step = 5;
    $: years = Array.from({ length: (maxYear - minYear) / step + 1}, (_, i) => minYear + (i * step));

    $: highlightSliderStart = dateToCoordinates(highlightStart, minDate, maxDate, containerHeight);
    $: highlightSliderEnd = dateToCoordinates(highlightEnd, minDate, maxDate, containerHeight);


    let temporalCoverageStart = $queryTemporalCoverage['start_time'] || minDate;
    let temporalCoverageEnd = $queryTemporalCoverage['end_time'] || maxDate;

    let temporalCoverageStartDate;
    let temporalCoverageEndDate;

    let rangeSliderStart;
    let rangeSliderEnd;

    export function displayTemporalCoverage(start, end) {
        // TODO validation logic: check start < end, set minStart, maxEnd

        if (start !== undefined && end !== undefined) {
            highlightStart = new Date(start);
            highlightEnd  = new Date(end);

        }
    }

    export function hideTemporalCoverage() {
        highlightStart = undefined;
        highlightEnd = undefined;
    }

    function syncTemporalCoverageStart(newTemporalCoverageStart) {
        temporalCoverageStart = newTemporalCoverageStart;

        const newQueryTemporalCoverage = $queryTemporalCoverage;
        newQueryTemporalCoverage['start_time'] = temporalCoverageStart;
        queryTemporalCoverage.set(newQueryTemporalCoverage);

        temporalCoverageStartDate = formattedDate(temporalCoverageStart);
        rangeSliderStart = dateToCoordinates(temporalCoverageStart, minDate, maxDate, containerHeight);
    }

    function syncTemporalCoverageEnd(newTemporalCoverageEnd) {
        temporalCoverageEnd = newTemporalCoverageEnd;

        const newQueryTemporalCoverage = $queryTemporalCoverage;
        newQueryTemporalCoverage['end_time'] = temporalCoverageEnd;
        queryTemporalCoverage.set(newQueryTemporalCoverage);

        temporalCoverageEndDate = formattedDate(temporalCoverageEnd);
        rangeSliderEnd = dateToCoordinates(temporalCoverageEnd, minDate, maxDate, containerHeight);
    }

    syncTemporalCoverageStart(temporalCoverageStart);
    syncTemporalCoverageEnd(temporalCoverageEnd);

    function dateToCoordinates(date, dateMin, dateMax, rangeLength) {
        return timeLinePadding + (Date.parse(date) - Date.parse(dateMin)) / (Date.parse(dateMax) - Date.parse(dateMin)) * (rangeLength - 2*timeLinePadding);
    }

    function coordinatesToDate(x, xmin, xmax, dateMin, dateMax) {
        return new Date(Date.parse(dateMin) + (x - xmin) / (xmax - xmin) * (Date.parse(dateMax) - Date.parse(dateMin)));
    }

    function getMousePositionInSVGSpace(evt, coordinateTransformMatrix) {
        if (coordinateTransformMatrix !== undefined) {
            return {
                x: (evt.clientX - coordinateTransformMatrix.e) / coordinateTransformMatrix.a,
                y: (evt.clientY - coordinateTransformMatrix.f) / coordinateTransformMatrix.d
            };
        }
        // const CTM = evt.target.getScreenCTM();
    }

    function formattedDate(date){
        const year = String(date.getUTCFullYear());
        const month = String(date.getUTCMonth() + 1).padStart(2, "0");
        const day = String(date.getUTCDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    function createDraggable(params) {
        let {xmin, ymin, xmax, ymax, x, y} = params;

        if (xmin === undefined) {
            xmin = -Infinity;
        }

        if (xmax === undefined) {
            xmax = Infinity;
        }

        if (ymin === undefined) {
            ymin = -Infinity;
        }

        if (ymax === undefined) {
            ymax = Infinity;
        }
        function moveTo(newX, newY) {
           x = Math.max(Math.min(xmax, newX), xmin);
           y = Math.max(Math.min(ymax, newY), ymin);
        }

        return Object.freeze({x, y, moveTo});
    }

    onMount(() => {
        const svg_container = document.getElementById("timeline-container");
        if (svg_container !== undefined) {
            coordinateTransformMatrix = svg_container.getScreenCTM();
        }

        leftRangeSlider = document.getElementById("range-slider-left");
        rightRangeSlider = document.getElementById("range-slider-right");


    });


    function startDrag(event) {
        const coords = getMousePositionInSVGSpace(event, coordinateTransformMatrix);
        // console.log(coords.x + ", " + coords.y);


        const draggableCandidates = Array.from([leftRangeSlider, rightRangeSlider])
            .filter((el) => {
                const bbox = el.getBBox();
                const xmin = bbox.x - 2;
                const xmax = bbox.x + bbox.width + 2;

                const ymin = bbox.y - 2;
                const ymax = bbox.y + bbox.height + 2;

                return coords.x >= xmin && coords.x <= xmax && coords.y >= ymin && coords.y <= ymax;
            });

        // console.log(draggableCandidates);

        // draggableCandidates


        if (draggableCandidates.length > 0) {
            // console.log("DRAGGABLE CANDIDATES FOUND");
            selectedElement = draggableCandidates[0];
            dragStartY = coords.y;
            dragYOffset = 0;
        }
        // event.preventDefault();
        //
        // dragStartX = timeRangeStart;
        // dragXOffset = 0;
        // console.log(JSON.stringify(dragStartX));
        // console.log("DRAG STARTED");
    }

    function drag(event) {
        // event.preventDefault();
        // console.log(selectedElement);
        // console.log(event.movementX);
        //
        if (selectedElement !== undefined && dragStartY !== undefined && dragYOffset !== undefined) {
            dragYOffset += event.movementY;
            // dragXOffset += Math.min(Math.max(event.movementX;, 5), timeRangeEnd - 20)
            // console.log("dragYOffset " + dragYOffset);
            const newPositionCandidate = dragStartY + dragYOffset;

            if (selectedElement.id === 'range-slider-left') {
                const newRangeSliderStart = Math.min(Math.max(newPositionCandidate, timeLinePadding), rangeSliderEnd - 20);
                const newTemporalCoverageStart = coordinatesToDate(newRangeSliderStart, timeLinePadding, containerHeight - timeLinePadding, minDate, maxDate);
                // console.log(newTemporalCoverageStart);
                syncTemporalCoverageStart(newTemporalCoverageStart);
            }

            if (selectedElement.id === 'range-slider-right') {
                const newRangeSliderEnd = Math.min(Math.max(newPositionCandidate, rangeSliderStart + 20), containerHeight - timeLinePadding);
                const newTemporalCoverageEnd = coordinatesToDate(newRangeSliderEnd, timeLinePadding, containerHeight - timeLinePadding, minDate, maxDate);
                syncTemporalCoverageEnd(newTemporalCoverageEnd);
            }
            // const xmin = 5;
            // const xmax = timeRangeEnd - 20;


            // console.log(dragXOffset);
            // console.log(parseFloat(selectedElement.getAttributeNS(null, "x")));
        }
    }

    function endDrag(event) {
        // event.preventDefault();
        // console.log(JSON.stringify(dragStartX));
        selectedElement = undefined;
        dragStartY = undefined;
        dragYOffset = undefined;
        // console.log(JSON.stringify(event));
    }

    function handleDateInput(value, targetType) {

        const parsedDate = new Date(value);
        const year = parsedDate.getUTCFullYear();

        // if value is not a valid date, parsedDate.getUTCFullYear() returns NaN
        if (!Number.isNaN(year)) {
            if (targetType === 'temporalCoverageStart') {
                const isValidDate = Date.parse(parsedDate) < Date.parse(temporalCoverageEnd) && year >= minYear;
                if (isValidDate) {
                    syncTemporalCoverageStart(parsedDate);
                } else {
                    syncTemporalCoverageStart(temporalCoverageStart);
                }
            }

            else if (targetType === 'temporalCoverageEnd') {
                const isValidDate = year <= maxYear && Date.parse(parsedDate) > Date.parse(temporalCoverageStart);
                if (isValidDate) {
                    syncTemporalCoverageEnd(parsedDate);
                } else {
                    syncTemporalCoverageEnd(temporalCoverageEnd);
                }
            }
        }


    }
</script>

<style>
    .timeline-container {
        border: 1px solid #ddd;
        border-radius: 2px;
        /*padding: 5px;*/
        margin-left: 10px;
    }

    .timeline {
        display: grid;
        grid-template-columns: 150px 200px;
        grid-template-rows: auto;
        grid-template-areas:
                "left right";

        margin: 5px;
        width: 350px;
        height: 300px;
        background-color: #fff;
        /*height: 200px;*/
        /*position: absolute;*/
        /*display: flex;*/
        /*align-items: center;*/
    }

    #timeline-container {
        grid-area: left;
    }

    #range-slider-left {
        cursor: row-resize;
    }

    #range-slider-right {
        cursor: row-resize;
    }

    .rangeSliderLine {
        stroke: #999;
        stroke-width: 2;
    }

    .rangeSliderCircle {
        /*stroke: -internal-root-color;*/
        stroke: #fff;
        fill: #999;
        r: 2;
        stroke-width: 1;
        cx: 0;
        cy: 0;
    }

    .axisLabel {
        font-weight: lighter;
        font-size: x-small;
        user-select: none;
    }

    .highlightLabel {
        /*font-weight: normal;*/
        font-size: small;
        user-select: none;
    }

    .form-row {
        padding-left: 5px;
        padding-right: 5px;
        margin-bottom: 10px;
        height: 30px;
        /*display: flex;*/
        /*justify-content: flex-start;*/
        /*flex-direction: column;*/
        /*flex-wrap: wrap;*/
    }

    /*.form-row input {*/
    /*    background-color: #FFFFFF;*/
    /*    border: 1px solid #D6D9DC;*/
    /*    border-radius: 3px;*/
    /*    width: 100%;*/
    /*    padding: 7px;*/
    /*    font-size: 14px;*/
    /*}*/

    .form-row label {
        margin-bottom: 5px;
    }

</style>

<div class="timeline-container">
    <div class="timeline">
    <span style="display: flex; flex-direction: column; height: 300px; grid-area: right">
        <div class="form-row" style="flex: 70%; align-self: flex-start">
            <label for="temporal-coverage-start">Temporal Coverage Start:</label>
            <input id="temporal-coverage-start" type="date" name="Temporal Coverage Start Date"
                   bind:value={temporalCoverageStartDate} placeholder="yyyy-mm-dd"
                   on:input="{(e) => handleDateInput(e.target.value, 'temporalCoverageStart')}">
        </div>

        <div class="form-row" style="flex: 25%; align-self: flex-end">
            <label for="temporal-coverage-end">Temporal Coverage End:</label>
            <input id="temporal-coverage-end" type="date" name="Temporal Coverage End Date"
                   bind:value={temporalCoverageEndDate} placeholder="yyyy-mm-dd"
                   on:input="{(e) => handleDateInput(e.target.value, 'temporalCoverageEnd')}">
        </div>
    </span>


        <svg id="timeline-container" height={containerHeight} width={containerWidth}
             on:mousedown={startDrag}
             on:mousemove={drag}
             on:mouseup={endDrag}
        >
            <rect x="0" y="0" height="{rangeSliderEnd - rangeSliderStart}" width="{timeLine}" style="fill:#999;fill-opacity:0.2;z-index: -1000" transform="translate(0, {rangeSliderStart})"/>

            <!--        <g id="rangeSliderLeft" x="0" y="0" width="10" height="{timeLine/2}" transform="translate({rangeSliderStart}, {timeLine/2})">-->
            <g id="range-slider-left">
                <!--            <line class="rangeSliderLine draggable" x1="0" x2="0" y1="{timeLine/2}" y2="{timeLine}"/>-->
                <!--            <circle class="rangeSliderCircle draggable"/>-->
                <line class="rangeSliderLine" y1="0" y2="0" x1="0" x2="{timeLine}" transform="translate(0, {rangeSliderStart})"/>
                <!--            <circle class="rangeSliderCircle" transform="translate({rangeSliderStart}, {timeLine})" />-->
            </g>


            <g id="range-slider-right">
                <line class="rangeSliderLine" y1="0" y2="0" x1="0" x2="{timeLine}" transform="translate(0, {rangeSliderEnd})"/>
                <!--            <circle class="rangeSliderCircle" transform="translate({rangeSliderEnd}, {timeLine})" />-->
            </g>

            <line y1="0" x1={timeLine} y2={containerHeight} x2={timeLine} style="stroke:#444;stroke-width:5"></line>

            {#each years as year}
            <circle class="rangeSliderCircle" transform="translate({timeLine}, {dateToCoordinates(year, minYear, maxYear, containerHeight)})"></circle>
            <text x="0" y="0" class="axisLabel" transform="translate({timeLine + 7}, {dateToCoordinates(year, minYear, maxYear, containerHeight) + 3.5})">{year}</text>
            {/each}

            {#if (highlightStart !== undefined && highlightEnd !== undefined)}
            {console.log(highlightStart > containerHeight/2)}
            {#if (highlightStart > containerHeight/2)}
            <line y1="{highlightSliderStart + 1}" y2="{highlightSliderStart}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderStart + 1}" y2="{containerHeight/2 - 25}" x1="{timeLine * 0.25 + 75}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{containerHeight/2 - 25}" y2="{containerHeight/2 - 25}" x1="{timeLine * 0.25 + 75}" x2="{timeLine * 0.25 + 86}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>

            <line y1="{highlightSliderEnd - 1}" y2="{highlightSliderEnd}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 80}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderEnd + 1}" y2="{containerHeight/2 + 15}" x1="{timeLine * 0.25 + 80}" x2="{timeLine * 0.25 + 80}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{containerHeight/2 + 15}" y2="{containerHeight/2 + 15}" x1="{timeLine * 0.25 + 80}" x2="{timeLine * 0.25 + 85}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>

            {:else if (highlightEnd < containerHeight/2)}
            <line y1="{highlightSliderStart + 1}" y2="{highlightSliderStart}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 80}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderStart + 1}" y2="{containerHeight/2 - 20}" x1="{timeLine * 0.25 + 80}" x2="{timeLine * 0.25 + 80}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderEnd - 1}" y2="{highlightSliderEnd}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderEnd + 1}" y2="{containerHeight/2 + 20}" x1="{timeLine * 0.25 + 75}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>

            {:else}
            <line y1="{highlightSliderStart + 1}" y2="{highlightSliderStart}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderStart + 1}" y2="{containerHeight/2 - 20}" x1="{timeLine * 0.25 + 75}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderEnd - 1}" y2="{highlightSliderEnd}" x1="{timeLine * 0.25}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            <line y1="{highlightSliderEnd + 1}" y2="{containerHeight/2 + 20}" x1="{timeLine * 0.25 + 75}" x2="{timeLine * 0.25 + 75}" style="stroke: #111; stroke-dasharray: 5,5; stroke-width: 1px; stroke-opacity: 0.4"/>
            {/if}


            <rect y="{highlightSliderStart}" x="{timeLine * 0.25}" height="{highlightSliderEnd - highlightSliderStart}" width="{timeLine * 0.75}" style="fill:#333;fill-opacity:0.2"/>
            <text y="{containerHeight/2 - 20}" x="{timeLine * 0.25}" class="highlightLabel" transform="translate({timeLine * 0.25 + 75}, 0)">{highlightStart.toLocaleDateString()}</text>
            <text y="{containerHeight/2 + 20}" x="{timeLine * 0.25}" class="highlightLabel" transform="translate({timeLine * 0.25 + 75}, 0)">{highlightEnd.toLocaleDateString()}</text>

            {/if}
        </svg>
    </div>
</div>
