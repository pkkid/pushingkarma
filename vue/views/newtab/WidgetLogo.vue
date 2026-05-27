<template>
  <a id='logowidget' :class='{fullscreen}' href='/' aria-label='Go to homepage'/>
</template>

<script setup>
  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
  })
</script>

<style>
  #logowidget {
    --logo-color: color-mix(in srgb, var(--darkbg-fg1), #000 20%);
    display: block;
    aspect-ratio: 1/1;
    background-color: var(--logo-color);
    mask: url('/static/img/pk.svg') no-repeat center/contain;
    transition: filter 0.2s ease;
    cursor: pointer;
    position: absolute;
    isolation: isolate;
    top: 20px; left: 20px;
    width: 80px;
  }
  #logowidget:hover {
    filter: brightness(1.08);
    &::before { opacity: 0.8; }
  }
  #newtab.fullscreen #logowidget {
    width: 100px;
    top: 40px;
    left: 40px;
  }
</style>
