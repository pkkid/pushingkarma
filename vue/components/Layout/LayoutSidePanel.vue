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
  /* LayoutSidePanel */
  .layoutsidepanel {
    --sidepanelwidth: v-bind(width);
    --sidepanelheight: calc(100vh - var(--navheight));
    .sidepanel-panel {
      width: var(--sidepanelwidth);
      height: var(--sidepanelheight);
      position: fixed;
      z-index: 11;
    }
    .sidepanel-content {
      padding-left: var(--sidepanelwidth);
      min-height: var(--sidepanelheight);
    }
  }

  /* SidePanel Menus */
  .sidepanel-panel:has(.menu) {
    overflow-y: auto;
    overscroll-behavior: contain;
    .menu {
      color: var(--linkcolor);
      margin-bottom: 30px;
      margin-top: 30px;
      .item {
        border-bottom: 0px solid #0000;
        border-left: 3px solid transparent;
        display: block;
        font-size: 16px;
        margin-top: 20px;
        overflow: hidden;
        padding: 10px 20px;
        text-overflow: ellipsis;
        transition: all 0.3s ease;
        white-space: nowrap;
      }
      .subitem {
        border-left: 3px solid transparent;
        color: var(--fgcolor60);
        display: block;
        font-size: 12px;
        min-height: 27px;
        padding: 3px 20px 3px 57px;
        transition: all 0.3s ease;
      }
      .link:hover, .link:focus, .link.selected {
        background-color: #fff1;
        border-left: 3px solid var(--accent);
        color: var(--fgcolor);
        cursor: pointer;
        user-select: none;
      }
      .mdi {
        font-size: 22px;
        margin-right: 10px;
        position: relative;
        top: 2px;
      }
    }
  }

  /* SidePanel Search Input */
  .sidepanel-panel .searchwrap {
    position: relative;
    display: flex;
    align-items: center;
    .searchinput, .searchinput:focus {
      background-color: #0003;
      border-radius: 0px;
      border-width: 0px;
      box-shadow: none;
      color: var(--accent);
      line-height: 40px;
      outline: none;
      padding: 0px 30px 0px 38px;
      width: 100%;
    }
    .mdi.mdi-magnify {
      position: absolute;
      font-size: 19px;
      left: 10px;
    }
    .mdi.mdi-close {
      position: absolute;
      font-size: 14px;
      right: 10px;
      transition: opacity 0.3s ease;
    }
  }
</style>
