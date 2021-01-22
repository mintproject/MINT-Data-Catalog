<script>
    export let key;
    export let val;

    function format_value(value) {
        if (String(value).substring(1, 10).includes("://")) {
            return `<a href=${value} target="_blank">${value}</a>`
        } else {
            return value;
        }
    }
</script>

<style>
    span {
        padding: 0 0 0 1.5em;
        background: 0 0.1em no-repeat;
        background-size: 1em 1em;
    }
</style>

<span>
    <strong>{key}</strong>: {@html format_value(val)}
</span>