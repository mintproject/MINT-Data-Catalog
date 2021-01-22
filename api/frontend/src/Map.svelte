<script>
    import { onMount } from 'svelte';
    import { mapbox, key } from './mapbox.js';
    import MapboxDraw from '@mapbox/mapbox-gl-draw';

    import {querySpatialCoverage} from "./stores";

    export let lat;
    export let lon;
    export let zoom;


    export function displayGeoJSON(geometry){
        map.addLayer({
            'id': 'datasetSpatialCoverage',
            'type': 'fill',
            'source': { 'type': 'geojson', 'data': {'type': 'Feature', 'geometry': geometry } },
            'layout': {},
            'paint': {
                'fill-color': '#333',
                'fill-opacity': 0.4
            }
        });
    }

    export function hideGeoJSON() {
        if (map.getLayer('datasetSpatialCoverage') !== undefined) {
            map.removeLayer('datasetSpatialCoverage');
        }

        if (map.getSource('datasetSpatialCoverage') !== undefined) {
            map.removeSource('datasetSpatialCoverage');
        }
    }

    let container;
    let map;

    onMount(() => {
        // const link = document.createElement('link');
        // link.rel = 'stylesheet';
        // link.href = 'https://cdnjs.cloudflare.com/ajax/libs/mapbox-gl/1.4.0/mapbox-gl.css';


        map = new mapbox.Map({
            container: document.getElementById("map"),
            style: 'mapbox://styles/mapbox/streets-v9',
            center: [lon, lat],
            zoom
        });

        const draw = new MapboxDraw({
            displayControlsDefault: false,
            controls: {
                polygon: true,
                trash: true
            }
        });
        map.addControl(draw);

        map.on('draw.create', setQuerySpatialCoverage);
        map.on('draw.delete', deleteQuerySpatialCoverage);
        map.on('draw.update', setQuerySpatialCoverage);



        function setQuerySpatialCoverage(e) {
            const data = draw.getAll();
            const geoJsonFeature = data["features"][0];
            if (geoJsonFeature !== undefined){
                const geoJson = geoJsonFeature['geometry'];
                querySpatialCoverage.set(geoJson);
            }

        }

        function deleteQuerySpatialCoverage(e) {
            querySpatialCoverage.set({})
        }

        document.getElementById('map').style.height = '300px';
        document.getElementById('map').style.width = '500px';

        return () => {
            map.remove();
            link.parentNode.removeChild(link);
        };
    });

</script>

<style>
    .map-wrapper {
        border: 1px solid #ddd;
        border-radius: 2px;
        margin-left: 20px;
        box-sizing: border-box;
    }
    #map {
        margin: 10px;
        width: 500px;
        height: 300px;
        box-sizing: border-box;
    }
</style>

<div class="map-wrapper">
    <div id="map">
        {#if map}
        <slot></slot>
        {/if}
    </div>
</div>
