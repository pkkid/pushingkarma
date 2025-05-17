<template>
  <div class='toc' v-if='headings?.length >= 1'>
    <h2 style='margin-top:30px;'>Table of Contents</h2>
    <div class='submenu'>
      <router-link class='h1' to=''>{{title}}</router-link>
      <template v-for='heading in headings' v-bind:key='heading.text'>
        <div><router-link :class='heading.tag' :to='{hash:heading.id}'>{{heading.text}}</router-link></div>
      </template>
    </div>
  </div>
</template>

<script setup>
  const props = defineProps({
    title: {type:String, required:false},
    headings: {type:Array, required:false},
  })
</script>

<style>
  .toc .submenu {
    .h1 { margin-left:0px; }
    .h2 { margin-left:0px; }
    .h3 { margin-left:15px; }
  }
</style>
