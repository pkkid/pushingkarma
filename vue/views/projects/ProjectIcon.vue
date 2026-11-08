<template>
  <span v-if='isSvg' class='projecticon svg' :style='style' v-html='icon' aria-hidden='true'/>
  <i v-else class='projecticon mdi' :class='icon || FALLBACK' :style='style' aria-hidden='true'/>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    project: {type:Object, required:true},  // Project with its GitHub stats from useProjects
    colored: {type:Boolean, default:true},  // Use the project color (false inherits the text color)
  })
  const FALLBACK = 'mdi-source-repository'  // Icon for projects without one set in the database
  const icon = computed(() => props.project.github?.icon)
  const isSvg = computed(() => icon.value?.trim().startsWith('<svg'))
  const style = computed(() => props.colored && props.project.github?.color ? {color:props.project.github.color} : {})
</script>

<style>
  .projecticon.svg {
    display: inline-block;
    height: 1em;
    line-height: 1;
    width: 1em;
    svg { display:block; fill:currentColor; height:100%; width:100%; }
  }
</style>
