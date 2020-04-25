<!--
Scroll Box - Custom vertical scrollbars for a container. I tried my best to
  style this for both dark and light backgrounds, but it may need some tweaking.
  The scrollbar itself will auto-hide when not hovered over the content.
-->
<template>
  <div class='scrollbox'>
    <div class='scrollbox-content'>
      <slot>scrollbox-content</slot>
    </div>
  </div>
</template>

<style lang='scss'>
  .scrollbox {
    overflow-x: hidden;
    visibility: hidden;
    height: calc(100vh - 100px);
    transition: visibility 0s 0.2s;
    width: 300px;
    &::-webkit-scrollbar { width: 10px; }
    &::-webkit-scrollbar-thumb {
      background: rgba($darkbg-bg4, 0.8);
      border-radius: 5px;
      border: 2px solid $darkbg-color;
    }
  }
  .scrollbox:hover,
  .scrollbox-content {
    visibility: visible;
  }
</style>

