<template>
  <div class='sortableitem' draggable='true'>
    <div class='grip'/>
    <slot></slot>
  </div>
</template>

<script setup>

</script>

<style>
  .sortableitem {
    border-top: 1px solid var(--lightbg-bg3);
    padding: 5px 10px 5px 25px;
    position: relative; 
    &:first-child { border-top: none; }

    .grip {
      color: var(--lightbg-fg3);
      content: '⋮';
      cursor: grab;
      font-size: 20px;
      margin-right: 10px;
      position: absolute;
      top: 0px; left: 10px;
    }
  }
</style>
