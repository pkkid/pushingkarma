<template>
  <div id='sidepanel'>
    <div class='sidepanel-panel darkbg'>
      <slot name='panel'>SidePanel #panel</slot>
    </div>
    <div class='sidepanel-content lightbg'>
      <slot name='content'>SidePanel #content</slot>
    </div>
  </div>
</template>

<style>
  #sidepanel {
    --sidepanelwidth: 300px;
    --sidepanelheight: calc(100vh - var(--navheight));
    .sidepanel-panel {
      width: var(--sidepanelwidth);
      height: var(--sidepanelheight);
      position: fixed;
    }
    .sidepanel-content {
      padding-left: var(--sidepanelwidth);
      min-height: var(--sidepanelheight);
    }
  }
</style>