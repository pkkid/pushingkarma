<template>
  <div class='widget filesystem-widget'>
    <div class='widget-title'>Filesystem</div>
    <div v-for='mount in mounts' :key='mount.mnt_point' class='mount'>
      <div class='mount-header'>
        <span class='mnt'>{{mount.mnt_point}}</span>
        <span class='sizes'>{{mount.usedGB}} / {{mount.totalGB}} GB</span>
      </div>
      <div class='bar-track'>
        <div class='bar-fill' :style='{width: mount.percent + "%", backgroundColor: barColor(mount.percent)}'/>
      </div>
      <div class='mount-pct'>{{mount.percent.toFixed(1)}}%</div>
    </div>
    <div v-if='!mounts.length' class='no-data'>No data</div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import useGlances from '@/composables/useGlances'

  const {data} = useGlances()

  const GB = 1024 ** 3

  const mounts = computed(function() {
    const fs = data.value?.fs || []
    const seen = new Set()
    return fs
      .filter(function(m) {
        // Skip duplicate devices (e.g. /home on same btrfs partition)
        if (seen.has(m.device_name)) return false
        seen.add(m.device_name)
        return true
      })
      .map(function(m) {
        const lastPart = m.mnt_point.split('/').filter(Boolean).pop()
        return {
          mnt_point: m.alias || lastPart || m.mnt_point,
          usedGB: (m.used / GB).toFixed(1),
          totalGB: (m.size / GB).toFixed(1),
          percent: m.percent,
        }
      })
  })

  function barColor(pct) {
    if (pct >= 90) return 'rgba(204,36,29,0.85)'
    if (pct >= 75) return 'rgba(215,153,33,0.85)'
    return 'rgba(69,133,136,0.85)'
  }
</script>

<style>
  .filesystem-widget {
    .mount { margin-bottom: 10px; }
    .mount-header {
      display: flex;
      justify-content: space-between;
      font-size: 1em;
      margin-bottom: 4px;
    }
    .mnt { opacity: 0.75; }
    .sizes { opacity: 0.55; font-size: 0.9em; }
    .bar-track {
      height: 10px;
      background: rgba(255,255,255,0.1);
      border-radius: 5px;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 0.3s ease;
    }
    .mount-pct { font-size: 0.85em; opacity: 0.45; text-align: right; margin-top: 2px; }
    .no-data { opacity: 0.4; font-size: 1em; }
  }
</style>
