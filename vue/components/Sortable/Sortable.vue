<template>
  <div class='sortable' :data-group='group' @sort='emit("sort", $event.detail)'>
    <slot></slot>
  </div>
</template>

<script setup>
  const emit = defineEmits(['sort'])
  const props = defineProps({
    group: {type:String, required:true},
  })
</script>

<style>
  .sortable {
    background-color: var(--lightbg-bg0);
    border: 1px solid var(--lightbg-bg3);
    border-radius: 6px;
    overflow: hidden;
  }
</style>
