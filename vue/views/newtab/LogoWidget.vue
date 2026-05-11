<template>
  <div id='logowidget' :class='{fullscreen}'/>
</template>

<script setup>
  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
  })
</script>

<style>
  #logowidget {
    aspect-ratio: 1/1;
    background-color: color-mix(in srgb, var(--darkbg-fg1), #000 20%);
    mask: url('/static/img/pk.svg') no-repeat center/contain;
    position: absolute;
    top: 20px; left: 20px;
    width: 80px;
    &.fullscreen {
      width: 100px;
      top: 40px;
      left: 40px;
    }
  }
</style>
