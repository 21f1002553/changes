<!-- src/App.vue -->
<template>
  <div id="app">
    <div class="background-wrapper">
      <!-- Route-matched component will appear here -->
      <router-view />
    </div>
  </div>
</template>

<script setup>
// No imports necessary here. Routing handles component display.
</script>

<style scoped>

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
    -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

</style>
