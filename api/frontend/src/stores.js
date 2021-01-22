import { writable } from 'svelte/store';

export let querySpatialCoverage;
export let datasetNameSearch;
export let datasetSpatialCoverage;
export let queryTemporalCoverage;

if (typeof window !== "undefined") {
    // means we are client-side
    datasetNameSearch = writable(localStorage.getItem("datasetNameSearch") || "");
    querySpatialCoverage = writable(localStorage.getItem("querySpatialCoverage") || {});
    datasetSpatialCoverage = writable(localStorage.getItem("datasetSpatialCoverage") || {});
    queryTemporalCoverage = writable(localStorage.getItem("queryTemporalCoverage") || {});
} else {
    // means we are server-side
    datasetNameSearch = writable("");
    querySpatialCoverage = writable({});
    datasetSpatialCoverage = writable({});
    queryTemporalCoverage = writable({});
}