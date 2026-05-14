<template>
  <div id='networkwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Network</div>
      <div class='values'>
        <span class='up'>↑</span> {{utils.formatSpeed(sumNetwork().up)}}
        <span class='delim'>|</span>
        <span class='down'>↓</span> {{utils.formatSpeed(sumNetwork().down)}}
      </div>
    </div>
    <!-- Charts -->
    <div class='chartrow'>
      <div class='chartwrap upload'>
        <div class='maxvalue'>{{utils.formatSpeed(glances.getMaxValue('upload'))}}</div>
        <Line v-if='updata' :data='updata' :options='OPTS' :plugins='[upChartPlugin]'/>
      </div>
      <div class='chartwrap download'>
        <div class='maxvalue'>{{utils.formatSpeed(glances.getMaxValue('download'))}}</div>
        <Line v-if='downdata' :data='downdata' :options='downopts' :plugins='[downChartPlugin]'/>
      </div>
    </div>
    <!-- Metrics -->
    <div class='metrics twocols'>
      <div><label>Local IP:</label> {{glances.data.ip?.address}}</div>
      <div><label>Connections:</label> {{glances.data.connections?.ESTABLISHED ?? '--'}}</div>
      <div><label>Ext IP:</label> {{glances.data.ip?.public_address}}</div>
      <div><label>Listening:</label> {{glances.data.connections?.LISTEN ?? '--'}}</div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line} from 'vue-chartjs'
  import {utils, sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const glances = useGlances()    // Glances composable
  const OPTS = sutils.LINEOPTS    // Base line chart options

  // Setup Upload Chart
  const upChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:1000, maxy:50000})
  glances.trackHistory('upload', 60, (d) => sumNetwork(d).up)

  // Setup Download Chart
  const downChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:1000, maxy:50000})
  const downopts = {...OPTS, scales: {...OPTS.scales, y:{...OPTS.scales.y, reverse:true}}}
  glances.trackHistory('download', 60, (d) => sumNetwork(d).down)

  // Sum Network
  // Sum sent and recv speeds across all interfaces, excluding loopback
  function sumNetwork(data) {
    var interfaces = data?.network || glances.data?.network || []
    return (interfaces || []).reduce(function(acc, iface) {
      if (iface.interface_name === 'lo') { return acc }
      acc.up += iface.bytes_sent_rate_per_sec || 0
      acc.down += iface.bytes_recv_rate_per_sec || 0
      acc.uptotal += iface.bytes_sent || 0
      acc.dntotal += iface.bytes_recv || 0
      return acc
    }, {up:0, down:0})
  }

  // Upload Data
  // Chart.js data object for Network Upload chart
  const updata = computed(function() {
    const h = glances.data?.history?.upload
    if (!h?.length) { return null }
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

  // Download Data
  // Chart.js data object for Network Download chart
  const downdata = computed(function() {
    const h = glances.data?.history?.download
    if (!h?.length) { return null }
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
</script>

<style>
  #networkwidget {
    .up { color: #d65d0e; }
    .down { color: #98971a; }

    .chartrow {
      gap: 0px !important;
      grid-template-rows: 80px 80px !important;
      .chartwrap.upload {
        border-bottom-right-radius: 0px;
        border-bottom-left-radius: 0px;
        border-bottom-width: 0px;
      }
      .chartwrap.download {
        border-top-right-radius: 0px;
        border-top-left-radius: 0px;
        border-top-width: 0px;
        .maxvalue {
          top: auto;
          bottom: 1px;
        }
      }
    }
  }
</style>
