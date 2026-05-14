<template>
  <div id='filesystemwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Filesystem</div>
    </div>
    <!-- Filesystems -->
    <div v-for='fs in glances.data?.fs' :key='fs.mnt_point' class='fs'>
      <span class='name'>{{getFsName(fs)}}</span>
      <span class='used'>
        {{fs.percent.toFixed(0)}}%
        <span style='margin:0px; opacity:0.8;'>of</span>
        {{utils.formatSize(fs.size, 0)}}
      </span>
      <div class='barbg'>
        <div class='barfg' :style='{width: fs.percent+"%", backgroundColor:getBarColor(fs.percent)}'/>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {utils, sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'

  const glances = useGlances()    // Glances composable

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
    if (pct >= 85) return sutils.COLORS.ORANGE
    return sutils.COLORS.GREEN
  }
</script>

<style>
  #filesystemwidget {

    .fs {
      margin-bottom: 15px;
      .used {
        float: right;
        font-size: 0.9em;
      }
      .barbg {
        height: 10px;
        background: #222;
        border-radius: 5px;
        overflow: hidden;
        .barfg {
          height: 100%;
          transition: width 0.3s ease;
        }
      }
    }
  }
</style>
