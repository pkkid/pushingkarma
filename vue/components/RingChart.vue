<template>
  <svg class='ringchart' :width='size' :height='size' :viewBox='`0 0 ${size} ${size}`'>
    <circle class='bg' :cx='center' :cy='center' :r='radius' :stroke='bgcolor' :stroke-width='thickness' fill='none' />
    <circle class='fg' :cx='center' :cy='center' :r='radius' :stroke='color' :stroke-width='thickness'
      :stroke-dasharray='circumference' :stroke-dashoffset='dashOffset' stroke-linecap='round' fill='none'
      transform='rotate(-90)' :transform-origin='`${center} ${center}`' />
    <text v-if='label' class='label' :x='center' :y='center' text-anchor='middle' dominant-baseline='central'>
      {{label}}
    </text>
  </svg>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    value: {default: 0},            // Current value
    max: {default: 100},            // Maximum value
    size: {default: 80},            // SVG width/height in px
    thickness: {default: 8},        // Ring stroke thickness
    color: {default: '#4a9eff'},    // Foreground arc color
    bgcolor: {default: 'rgba(255,255,255,0.12)'},  // Background ring color
    label: {default: null},         // Optional text inside the ring
  })

  const center = computed(() => props.size / 2)
  const radius = computed(() => (props.size - props.thickness) / 2)
  const circumference = computed(() => 2 * Math.PI * radius.value)
  const dashOffset = computed(() => {
    const pct = Math.min(Math.max(props.value / props.max, 0), 1)
    return circumference.value * (1 - pct)
  })
</script>

<style>
  .ringchart {
    display: block;
    flex-shrink: 0;
    .label {
      font-size: 0.9em;
      font-weight: bold;
      fill: currentColor;
    }
  }
</style>
