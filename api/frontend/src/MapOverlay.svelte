<script>
    import { getContext } from 'svelte';
    import { mapbox, key } from './mapbox.js';

    const { getMap } = getContext(key);
    const map = getMap();
</script>