<template>
  <div/>
</template>

<script setup>
  // Implements the Obsidian Image Gallery Plugin for MarkdownIt
  // https://github.com/lucaorio/obsidian-image-gallery
  import {onMounted, ref} from 'vue'

  const props = defineProps({
    path: {type:String, default:''},              // Path relative to the root of the vault
    type: {type:String, default:'horizontal'},    // Type of masonry (horizontal, vertical)
    gutter: {type:Number, default:8},             // Spacing in px between the images
    radius: {type:Number, default:0},             // Border radius in px of the images
    sortby: {type:String, default:'ctime'},       // Sort images by (ctime,	mtime, name)
    sort: {type:String, default:'desc'},          // Order of sorting (desc, asc)
    height: {type:Number, default:260},           // Horizontal type only; Height in px of all rows
    columns: {type:Number, default:3},            // Vertical type only; Number of columns for desktop
  })

  onMounted(function() {
    console.log(props)
  })

</script>
