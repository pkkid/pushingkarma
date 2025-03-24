<template>
  <div class='layoutsidepanel'>
    <div class='sidepanel-panel darkbg'>
      <slot name='panel'>SidePanel #panel</slot>
    </div>
    <div class='sidepanel-content lightbg'>
      <slot name='content'>SidePanel #content</slot>
    </div>
  </div>
</template>

<script setup>
  const props = defineProps({
    width: {type:String, default:'300px'},
  })
</script>

<style>
  .layoutsidepanel {
    --sidepanelwidth: v-bind(width);
    --sidepanelheight: calc(100vh - var(--navheight));
    .sidepanel-panel {
      width: var(--sidepanelwidth);
      height: var(--sidepanelheight);
      position: fixed;
      z-index: 98;
    }
    .sidepanel-content {
      padding-left: var(--sidepanelwidth);
      min-height: var(--sidepanelheight);
    }
  }
</style>
