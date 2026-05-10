<template>
  <div class='glances-widget memory-widget'>
    <div class='widget-title'>Memory</div>
    <div class='mem-layout'>
      <div class='chart-wrap'>
        <Doughnut v-if='ringData' :data='ringData' :options='ringOptions'/>
      </div>
      <div class='mem-stats'>
        <div><span class='label'>Used</span> {{usedGB}} GB</div>
        <div><span class='label'>Total</span> {{totalGB}} GB</div>
        <div><span class='label'>Free</span> {{freeGB}} GB</div>
        <div class='pct'>{{pct}}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Doughnut} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const {data} = useGlances()

  const GB = 1024 ** 3
  const fmt = v => (v / GB).toFixed(1)

  const mem = computed(() => data.value?.mem ?? null)
  const usedGB = computed(() => mem.value ? fmt(mem.value.used) : '--')
  const totalGB = computed(() => mem.value ? fmt(mem.value.total) : '--')
  const freeGB = computed(() => mem.value ? fmt(mem.value.available) : '--')
  const pct = computed(() => mem.value ? mem.value.percent.toFixed(1) : '--')

  const ringData = computed(function() {
    if (!mem.value) return null
    return {
      labels: ['Used', 'Free'],
      datasets: [{
        data: [mem.value.used, mem.value.available],
        backgroundColor: ['rgba(69,133,136,0.85)', 'rgba(255,255,255,0.1)'],
        borderWidth: 0,
      }],
    }
  })

  const ringOptions = {
    animation: {duration: 300},
    responsive: true,
    maintainAspectRatio: false,
    cutout: '72%',
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
  }
</script>

<style>
  .memory-widget {
    .mem-layout {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .chart-wrap { height: 90px; width: 90px; flex-shrink: 0; }
    .mem-stats {
      font-size: 1em;
      line-height: 1.8;
      opacity: 0.85;
      .label { opacity: 0.6; width: 52px; display: inline-block; }
      .pct { font-size: 2em; font-weight: 600; line-height: 1; margin-top: 4px; }
    }
  }
</style>
