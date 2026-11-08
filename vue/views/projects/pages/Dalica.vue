<template>
  <p class='lede'>
    Dalica is a local-first photo manager written in Rust. It works directly on the
    folders already on your disk, and is a modern, multiplatform tribute to the classic
    Picasa workflow.
  </p>
  <h2>Why I built it</h2>
  <p class='draft'>Motivation: what you missed about Picasa, what you tried in between,
    and the moment you decided to build your own.</p>
  <h2>Building it in Rust</h2>
  <p class='draft'>Experiences: learning Rust, the thumbnail pipeline, keeping everything
    local-first, and what turned out harder than expected.</p>
  <h2>Where it is now</h2>
  <p class='draft'>Status, supported platforms, what is next, and where to download it.</p>
</template>

<script setup>
  defineProps({project:{type:Object, required:true}})
</script>
