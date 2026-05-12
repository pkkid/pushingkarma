<template>
  <div id='cpuwidget' class='widget'>
    <div class='header-row'>
      <div class='title'>{{data?.system?.hostname || 'CPU'}}</div>
      <div class='values'>
        {{data?.cpu?.total?.toFixed(1) ?? '--'}}%
        <span>|</span>
        {{cputemp}}°C
      </div>
    </div>
    <!-- CPU Charts -->
    <div class='chartrow'>
      <div class='chartwrap cpu'>
        <span class='maxvalue'>100%</span>
        <Line ref='cpuref' v-if='cpudata' :data='cpudata' :options='cpuopts'/>
      </div>
      <div class='chartwrap core1'>
        <Bar v-if='coredata1' :data='coredata1' :options='baropts'/>
      </div>
      <div class='chartwrap core2'>
        <Bar v-if='coredata2' :data='coredata2' :options='baropts'/>
      </div>
      <div class='chartwrap cputemp'>
        <span class='maxvalue'>{{cputempmax}}°C</span>
        <Line ref='tempref' v-if='cputempdata' :data='cputempdata' :options='tempopts'/>
      </div>
    </div>
    <!-- Text rows -->
    <div class='stats-row' style='clear:left;'>
      <div class='stat-col'>
        <div>Freq: {{cpufreq}} GHz</div>
        <div>Uptime: {{ data?.uptime?.replace(/:\d+$/, '') || '--' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, ref, watch} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line, Bar} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  import chartScrollPlugin from '@/utils/chartscroll'
  import {COLORS, lineOpts, barOpts, scrollChart} from '@/utils/statsutils'
  Chart.register(...registerables, chartScrollPlugin())

  const {data, cpuHistory, tempHistory} = useGlances()
  const props = defineProps({
    animationDuration: {default: 300},    // Chart animation duration
    animationStyle: {default: 'ease'}     // Chart animation style
  })
  const cpuref = ref(null)                // Ref for CPU usage chart
  const tempref = ref(null)               // Ref for CPU temperature chart
  watch(cpuHistory, () => scrollChart(cpuref.value?.chart, props), {flush: 'post'})
  watch(tempHistory, () => scrollChart(tempref.value?.chart, props), {flush: 'post'})

  const cputemp = computed(function() {
    const sensors = data.value?.sensors || []
    const pkg = sensors.find(s => s.label === 'Package id 0')
    return pkg ? pkg.value : '--'
  })

  const cputempmax = computed(function() {
    const h = tempHistory.value
    const vals = h.map(p => p.value).filter(v => v > 0)
    return vals.length ? Math.max(...vals) : '--'
  })

  const cpufreq = computed(function() {
    const hz = data.value?.quicklook?.cpu_hz_current
    return hz ? (hz / 1e9).toFixed(2) : '--'
  })

  // Chart Options
  // Chart.js options for CPU usage, temperature, and core bar charts
  const cpuopts  = {...lineOpts, scales: {...lineOpts.scales, y:{...lineOpts.scales.y, max:100}}}
  const tempopts = {...lineOpts, scales: {...lineOpts.scales, y:{display:false, min:40}}}
  const baropts  = barOpts

  // CPU Data
  // Chart.js data object for CPU usage chart
  const cpudata = computed(function() {
    const h = cpuHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: COLORS.BLUE,
        backgroundColor: `${COLORS.BLUE}33`,
        fill: true,
      }],
    }
  })

  // CPU Temp Data
  // Chart.js data object for CPU temperature chart
  const cputempdata = computed(function() {
    const h = tempHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: COLORS.ORANGE,
        backgroundColor: `${COLORS.ORANGE}33`,
        fill: true,
      }],
    }
  })

  // Get Core Data
  // Helper function to get Chart.js data object for even or odd indexed cores
  const getCoreData = function(evenodd='even') {
    const mod = evenodd === 'even' ? 0 : 1
    const cores = data.value?.percpu.filter((_, i) => i % 2 == mod)
    if (!cores?.length) return null
    return {
      labels: cores.map((_, i) => i),
      datasets: [{
        data: cores.map(c => c.total),
        backgroundColor: COLORS.BLUE,
        borderRadius: 2,
      }],
    }
  }

  // Core Data
  // Even-indexed cores in one chart
  const coredata1 = computed(function() { return getCoreData('even') })
  const coredata2 = computed(function() { return getCoreData('odd') })
</script>

<style>
  #stats #cpuwidget {
    .chartrow {
      grid-template-columns: auto 150px;
      grid-template-rows: 50px 50px 70px;
      .cpu { grid-row:span 3; width:3fr; }
    }
  }
</style>
