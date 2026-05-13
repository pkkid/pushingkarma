<template>
  <div id='gpuwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>
        {{gpu?.name.replace('GeForce RTX', '') || 'GPU'}}
      </div>
      <div class='values'>
        {{gpu?.proc?.toFixed(0) ?? '--'}}%
        <span>|</span>
        {{gpu?.temperature?.toFixed(0) ?? 0}}°C
      </div>
    </div>
    <!-- Charts -->
    <div class='chartrow'>
      <div class='chartwrap gpu'>
        <span class='maxvalue'>100%</span>
        <Line v-if='gpudata' :data='gpudata' :options='gpuopts' :plugins='[gpuChartPlugin]'/>
      </div>
      <div class='chartwrap gpumem'>
        GPU Mem
      </div>
      <div class='chartwrap gputemp'>
        <span class='maxvalue'>{{glances.getMaxValue('gputemp')}}°C</span>
        <Line v-if='gputempdata' :data='gputempdata' :options='tempopts' :plugins='[tempChartPlugin]'/>
      </div>
    </div>
    <!-- Metrics -->
    <!-- <div class='metrics'>
      <div>
        <span class='name'>Freq:</span>
        <span class='value'>{{((glances.data.quicklook?.cpu_hz_current ?? 0) / 1e9).toFixed(2)}} GHz</span>
      </div>
      <div>
        <span class='name'>Uptime:</span>
        <span class='value'>{{ glances.data.uptime?.replace(/:\d+$/, '') || '--' }}</span>
      </div>
    </div> -->
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line} from 'vue-chartjs'
  import {sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const glances = useGlances()    // Glances composable
  const OPTS = sutils.LINEOPTS    // Base line chart options
  const gpu = computed(() => glances.data?.gpu?.[0] ?? null)

  // Setup GPU Usage Chart
  const gpuChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000})
  const gpuopts = {...OPTS, scales: {...OPTS.scales, y:{...OPTS.scales.y, max:100}}}
  glances.trackHistory('gpuusage', 60, (d) => d?.gpu?.[0]?.proc ?? 0)

  // Setup GPU Tempurature Chart
  const tempChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:300})
  const tempopts = {...OPTS, scales: {...OPTS.scales, y:{display:false, min:40}}}
  glances.trackHistory('gputemp', 30, (d) => d?.gpu?.[0]?.temperature ?? 0)

  // GPU Usage Data
  // Chart.js data object for CPU usage chart
  const gpudata = computed(function() {
    const h = glances.data?.history?.gpuusage
    if (!h?.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: sutils.COLORS.GREEN,
        backgroundColor: `${sutils.COLORS.GREEN}33`,
        fill: true,
      }],
    }
  })

  // GPU Tempurature Data
  // Chart.js data object for CPU temperature chart
  const gputempdata = computed(function() {
    const h = glances.data?.history?.gputemp
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
</script>

<style>
  #stats #gpuwidget {
    .chartrow {
      grid-template-columns: auto 150px;
      grid-template-rows: 50px 50px 70px;
      .gpu { grid-row:span 3; width:3fr; }
      .gpumem { grid-row:span 2; }
    }
  }
</style>
