<template>
  <div id='filesystemwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Filesystem</div>
      <div class='values'>{{utils.formatSpeed(sumDiskIO())}}</div>
    </div>
    <!-- Charts -->
    <div class='chartrow'>
      <div class='chartwrap diskio'>
        <div class='maxvalue'>{{utils.formatSpeed(glances.getMaxValue('diskio'))}}</div>
        <Line v-if='diskiodata' :data='diskiodata' :options='sutils.LINEOPTS' :plugins='[diskioChartPlugin]'/>
      </div>
    </div>
    <!-- Filesystems -->
    <div v-for='fs in glances.data?.fs' :key='fs.mnt_point' class='fs'>
      <span class='name'>{{getFsName(fs)}}</span>
      <span class='used'>
        {{fs.percent.toFixed(0)}}%
        <span class='delimtext'>of</span>
        {{utils.formatSize(fs.size, 3)}}
      </span>
      <div class='barbg'>
        <div class='barfg' :style='{width: fs.percent+"%", backgroundColor:getBarColor(fs.percent)}'/>
      </div>
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

  // Setup Disk IO Chart
  const diskioChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:1000, maxy:50000})
  glances.trackHistory('diskio', 60, (d) => sumDiskIO(d))

  // Sum Disk IO
  // Sum total read + write speed across all disk devices
  function sumDiskIO(data) {
    var disks = data?.diskio || glances.data?.diskio || []
    return (disks || []).reduce(function(acc, disk) {
      return acc + (disk.read_bytes_rate_per_sec || 0) + (disk.write_bytes_rate_per_sec || 0)
    }, 0)
  }

  // Disk IO Data
  // Chart.js data object for total disk IO chart
  const diskiodata = computed(function() {
    const h = glances.data?.history?.diskio
    if (!h?.length) { return null }
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

  // Get Filesystem Name
  // Use alias if available, otherwise use last part of mount point path
  const getFsName = function(fs) {
    if (fs.alias) { return fs.alias }
    const parts = fs.mnt_point.split('/').filter(Boolean)
    return parts.length ? parts.pop() : fs.mnt_point
  }

  // Get Bar Color
  // Return bar color based on usage percent
  const getBarColor = function(pct) {
    if (pct >= 85) { return sutils.COLORS.ORANGE }
    return sutils.COLORS.BLUE
  }
</script>

<style>
  #filesystemwidget {
    .fs {
      margin: 20px 0px;
      .used {
        float: right;
        font-size: 0.9em;
      }
      .barbg {
        height: 8px;
        background: #222;
        border-radius: 5px;
        overflow: hidden;
        .barfg {
          height: 100%;
          border-radius: 5px;
          transition: width 0.3s ease;
        }
      }
    }
  }
</style>
