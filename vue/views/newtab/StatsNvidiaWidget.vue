<template>
  <div class='widget nvidia-widget'>
    <div class='widget-title'>GPU: {{gpuName}}</div>
    <div class='chart-wrap'>
      <span class='current-value'>{{gpuProc}}%</span>
      <Line ref='lineRef' v-if='lineData' :data='lineData' :options='lineOptions' :plugins='[scrollPlugin]'/>
    </div>
    
    <div v-if='!hasGpu' class='no-gpu'>Not available</div>
    <template v-else>
      <div class='stats-row'>
        <div class='stat-col'>
          <div>Temp: {{gpuTemp}}°C</div>
          <div>VRAM: {{gpuMemRate}}%</div>
          <div></div>
        </div>
      </div>
      
    </template>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  import {COLORS, LINEOPTS, scrollingChartPlugin} from '@/utils/statutils'
  const {GREEN, GREEN_FILL} = COLORS
  const scrollPlugin = scrollingChartPlugin({animateXDuration: 300, animateXStyle: 'ease'})
  Chart.register(...registerables)

  const {data, trackHistory} = useGlances()
  trackHistory('gpuproc', 60, (d) => d?.gpu?.[0]?.proc ?? null)

  const gpu = computed(() => data.value?.gpu?.[0] ?? null)
  const hasGpu = computed(() => !!gpu.value)

  const gpuProc = computed(() => gpu.value?.proc?.toFixed(1) ?? '--')
  const gpuTemp = computed(() => gpu.value?.temperature ?? '--')
  const gpuMemRate = computed(() => gpu.value?.mem?.toFixed(1) ?? '--')
  const gpuName = computed(() => gpu.value?.name ?? '--')

  const lineOptions = {...LINEOPTS, scales: {...LINEOPTS.scales, y: {...LINEOPTS.scales.y, max: 100}}}

  const lineData = computed(function() {
    const h = (data.value?.history?.gpuproc||[]).filter(p => p.value !== null)
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: GREEN,
        backgroundColor: GREEN_FILL,
        fill: true,
      }],
    }
  })
</script>

<style>
  .nvidia-widget {
    .no-gpu { opacity: 0.4; font-size: 1em; }
    .stats-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 6px;
    }
    .stat-big { font-size: 3em; font-weight: 600; line-height: 1; }
    .stat-col { font-size: 0.95em; opacity: 0.75; line-height: 1.6; }
    .chart-wrap { height: 150px; width: 100%; }
  }
</style>
