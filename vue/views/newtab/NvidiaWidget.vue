<template>
  <div class='glances-widget nvidia-widget'>
    <div class='widget-title'>GPU</div>
    <div v-if='!hasGpu' class='no-gpu'>Not available</div>
    <template v-else>
      <div class='stats-row'>
        <span class='stat-big'>{{gpuProc}}%</span>
        <div class='stat-col'>
          <div>Temp: {{gpuTemp}}°C</div>
          <div>Mem: {{gpuMemUsed}} / {{gpuMemTotal}} MB</div>
          <div>Mem Rate: {{gpuMemRate}}%</div>
          <div>Driver: {{driver}}</div>
        </div>
      </div>
      <div class='chart-wrap'>
        <Line v-if='lineData' :data='lineData' :options='lineOptions'/>
      </div>
    </template>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const {data, gpuHistory} = useGlances()

  const GREEN = 'rgba(152,151,26,0.9)'
  const GREEN_FILL = 'rgba(152,151,26,0.2)'

  const gpu = computed(() => data.value?.gpu?.[0] ?? null)
  const hasGpu = computed(() => !!gpu.value)

  const gpuProc = computed(() => gpu.value?.proc?.toFixed(1) ?? '--')
  const gpuTemp = computed(() => gpu.value?.temperature ?? '--')
  const gpuMemUsed = computed(() => gpu.value ? Math.round(gpu.value.mem * gpu.value.mem_total / 100) : '--')
  const gpuMemTotal = computed(() => gpu.value?.mem_total ?? '--')
  const gpuMemRate = computed(() => gpu.value?.mem?.toFixed(1) ?? '--')
  const driver = computed(() => gpu.value?.driver_version ?? '--')

  const lineOptions = {
    animation: {duration: 300},
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0, max: 100},
    },
    elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 1.5}},
  }

  const lineData = computed(function() {
    const h = gpuHistory.value.filter(p => p.value !== null)
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
    .chart-wrap { height: 70px; width: 100%; }
  }
</style>
