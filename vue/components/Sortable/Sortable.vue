<template>
  <div class='sortable'>
    <slot></slot>
  </div>
</template>

<script setup>

</script>

<style>
  .sortable {
    background-color: var(--lightbg-bg0);
    border: 1px solid var(--lightbg-bg3);
    border-radius: 6px;
    padding: 1px;
  }
</style>
