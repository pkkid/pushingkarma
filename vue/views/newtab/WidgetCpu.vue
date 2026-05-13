<template>
  <div id='cpuwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>
        {{glances.data.system?.hostname || 'CPU'}}
      </div>
      <div class='values'>
        {{glances.data.cpu?.total?.toFixed(1) ?? '--'}}%
        <span>|</span>
        {{utils.findItem(glances.data?.sensors, 'label', 'Package id 0', 'value') ?? 0}}°C
      </div>
    </div>
    <!-- Charts -->
    <div class='chartrow'>
      <div class='chartwrap cpu'>
        <span class='maxvalue'>100%</span>
        <Line v-if='cpudata' :data='cpudata' :options='cpuopts' :plugins='[cpuChartPlugin]'/>
      </div>
      <div class='chartwrap core1'>
        <Bar v-if='coredata1' :data='coredata1' :options='sutils.BAROPTS'/>
      </div>
      <div class='chartwrap core2'>
        <Bar v-if='coredata2' :data='coredata2' :options='sutils.BAROPTS'/>
      </div>
      <div class='chartwrap cputemp'>
        <span class='maxvalue'>{{glances.getMaxValue('cputemp')}}°C</span>
        <Line v-if='cputempdata' :data='cputempdata' :options='tempopts' :plugins='[tempChartPlugin]'/>
      </div>
    </div>
    <!-- Metrics -->
    <div class='metrics'>
      <div>
        <span class='name'>Freq:</span>
        <span class='value'>{{((glances.data.quicklook?.cpu_hz_current ?? 0) / 1e9).toFixed(2)}} GHz</span>
      </div>
      <div>
        <span class='name'>Uptime:</span>
        <span class='value'>{{ glances.data.uptime?.replace(/:\d+$/, '') || '--' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line, Bar} from 'vue-chartjs'
  import {utils, sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const glances = useGlances()    // Glances composable
  const OPTS = sutils.LINEOPTS    // Base line chart options

  // Setup CPU Usage Chart
  const cpuChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000})
  const cpuopts = {...OPTS, scales: {...OPTS.scales, y:{...OPTS.scales.y, max:100}}}
  glances.trackHistory('cpuusage', 60, (d) => d?.cpu?.total ?? 0)

  // Setup CPU Tempurature Chart
  const tempChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:300})
  const tempopts = {...OPTS, scales: {...OPTS.scales, y:{display:false, min:40}}}
  glances.trackHistory('cputemp', 30, (d) => utils.findItem(d?.sensors, 'label', 'Package id 0', 'value') ?? 0)

  // CPU Usage Data
  // Chart.js data object for CPU usage chart
  const cpudata = computed(function() {
    const h = glances.data?.history?.cpuusage
    if (!h?.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: sutils.COLORS.BLUE,
        backgroundColor: `${sutils.COLORS.BLUE}33`,
        fill: true,
      }],
    }
  })

  // CPU Tempurature Data
  // Chart.js data object for CPU temperature chart
  const cputempdata = computed(function() {
    const h = glances.data?.history?.cputemp
    if (!h?.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: sutils.COLORS.ORANGE,
        backgroundColor: `${sutils.COLORS.ORANGE}33`,
        fill: true,
      }],
    }
  })

  // Get Core Data
  // Helper function to get Chart.js data object for even or odd indexed cores
  const getCoreData = function(evenodd='even') {
    const mod = evenodd === 'even' ? 0 : 1
    const cores = glances.data?.percpu?.filter((_, i) => i % 2 == mod)
    if (!cores?.length) return null
    return {
      labels: cores.map((_, i) => i),
      datasets: [{
        data: cores.map(c => c.total),
        backgroundColor: sutils.COLORS.BLUE,
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
