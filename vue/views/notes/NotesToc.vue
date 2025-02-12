<template>
  <div class='toc' v-if='headings?.length > 1'>
    <h2 style='margin-top:30px;'>Table of Contents</h2>
    <div class='submenu'>
      <div class='h1'><router-link to=''>{{title}}</router-link></div>
      <div v-for='heading in headings' v-bind:key='heading.text' :class='heading.tag'>
        <router-link :to='{hash:heading.id}'>{{heading.text}}</router-link>
      </div>
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
    .h1 { padding-left:0px; }
    .h2 { padding-left:0px; }
    .h3 { padding-left:15px; }
  }
</style>