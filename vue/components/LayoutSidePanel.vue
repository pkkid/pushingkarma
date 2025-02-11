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

<style>
  .layoutsidepanel {
    --sidepanelwidth: 300px;
    --sidepanelheight: calc(100vh - var(--navheight));
    .sidepanel-panel {
      width: var(--sidepanelwidth);
      height: var(--sidepanelheight);
      position: fixed;
      z-index: 100;
    }
    .sidepanel-content {
      padding-left: var(--sidepanelwidth);
      min-height: var(--sidepanelheight);
    }
  }
</style>