<template>
  <div class='sortable' :data-group='group' @sort='onSort'>
    <slot></slot>
  </div>
</template>

<script setup>
  const emit = defineEmits(['sort'])
  const props = defineProps({
    group: {type:String, required:true},
  })

  const onSort = function(event) {
    emit('sort', event.detail)
  }
</script>

<style>
  .sortable {
    background-color: var(--lightbg-bg0);
    border: 1px solid var(--lightbg-bg3);
    border-radius: 6px;
    padding: 1px;
  }
</style>
