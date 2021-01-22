<script>
    // import SearchForm from './SearchForm.svelte';
    // import RegistrationForm from './RegistrationForm.svelte';
    // export let sidebarOpen = false;

    let renderHeader = function inIframe() {
        try {
            return window.self === window.top;
        } catch (e) {
            // we are in an iframe, so no need to render header
            // https://stackoverflow.com/questions/326069/how-to-identify-if-a-webpage-is-being-loaded-inside-an-iframe-or-directly-into-t
            return false;
        }
    }();

    let path = window.location.pathname;
    // console.log(JSON.stringify(window.location));
    // console.log("in iframe? " + !renderHeader);

    import Router from './router';
</script>

<style>
    h1 {
        color: purple;
    }

    .app {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr); /* Side nav is hidden on mobile */
        grid-template-rows: 50px 1fr 50px;
        grid-template-areas:
                'sidenav header'
                'sidenav main'
                'sidenav footer';
        /*min-height: 100vh;*/
        /*height: 100%;*/
    }

    .sidenav {
        /*display: none;*/
        grid-area: sidenav;
        /*background-color: #64bfbc;*/
        background-color: #dddddd;
        /*display: flex;*/
        /*flex-direction: column;*/
        height: 100%;
        width: 50px;
        /*position: fixed;*/
        overflow-y: auto;
        box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.16), 0 0 0 1px rgba(0, 0, 0, 0.08);
        z-index: 2; /* Needs to sit above the hamburger menu icon */
        /*transform: translateX(-245px);*/
        transition: all .6s ease-in-out;
    }
    .sidenav.active {
        width: 250px;
        background-color: antiquewhite;
        /*transform: translate(0);*/
    }

    .main {
        grid-area: main;
        height: 100%;
        /*background-color: #dddddd;*/
    }

    header {
        /*display: inline-block;*/
        /*position: absolute;*/
        grid-area: header;
        align-self: stretch;
        align-items: center;
        background-color: #f5f5f5;
        /*text-align: center;*/
        /*padding: 1.5em;*/
    }
    header img {
        box-sizing: border-box;
        padding-left: 10px;
        padding-right: 10px;
        padding-top: 5px;
        padding-bottom: 5px;
        width: 100px;
        height: 100%;
    }

    header .title {
        font-size: 150%;
        margin-left: 5px;
        vertical-align: middle;
        position: absolute;
        line-height: 50px;
        /*display: grid;*/
        /*grid-template-columns: 10% 40% 50%; !* Side nav is hidden on mobile *!*/
        /*grid-template-areas: 'logo title right';*/
        /*align-content: center;*/
        /*justify-items: left;*/
        /*line-height: 40px;*/
        /*height: 40px;*/
        /*text-align: center;*/
    }

    header ul {
        float: right;
        display: inline;
        text-align: right;
        list-style: none;
        padding-right: 40px;
        padding-left: 25px;
    }
    header ul li {
        padding-right: 10px;
        display: inline-block;
    }
    header ul li a {
        color: #464647;
        text-align: center;
        font-size: 17px;
    }
    header ul li a:hover {
        /*background-color: #ddd;*/
        color: black;
    }
    .active {
        /*background-color: #4CAF50;*/
        font-weight: bolder;
    }

    main {
        padding: 1.5em;
    }
</style>

<div class="app">
    {#if renderHeader}
    <header class="header">
        <img class="logo" src="/mint_logo.png" alt="MINT Logo"/>
        <span class="title" >Data Catalog</span>
        <ul>
            <li><a href="/" class:active="{path === '/'}">Search</a></li>
            <li><a href="/documentation" class:active="{path.includes('documentation')}">API Documentation</a></li>
<!--            <li><a href="/registration" class:active="{path.includes('registration')}">Registration</a></li>-->
        </ul>
    </header>
    {/if}

<!--    <aside class="sidenav" class:active="{sidebarOpen}">-->
<!--    </aside>-->

    <main class="main">
        <svelte:component this={Router(path)}></svelte:component>
<!--        <RegistrationForm/>-->
<!--        <div><SearchForm/></div>-->
<!--        <button on:click={() => sidebarOpen = !sidebarOpen}>Toggle</button>-->
    </main>
</div>