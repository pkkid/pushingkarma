<template>
  <div id='memorywidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Memory</div>
    </div>
    <!-- Charts -->
    <div class='chartwrap mem' style='padding:10px; float:left; width:180px;'>
      <RingChart :value='glances.data?.mem?.percent ?? 0' :max='100' :size='150' :thickness='20'
        :color='sutils.COLORS.GREEN' bgcolor='#222' :label='`${glances.data?.mem?.percent?.toFixed(0)}%`'
        sublabel='Used'/>
    </div>
    <!-- Metrics -->
    <div class='metrics' style='float:left; margin-left:20px;'>
      <div><label>Used:</label> {{utils.formatSize(glances.data.mem?.used ?? 0)}}</div>
      <div><label>Total:</label> {{utils.formatSize(glances.data.mem?.total ?? 0)}}</div>
      <div><label>Available:</label> {{utils.formatSize(glances.data.mem?.available ?? 0)}}</div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {RingChart} from '@/components'
  import {utils, sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'

  const glances = useGlances()    // Glances composable
</script>

<style>
  #memorywidget {
    .chartwrap {
      border-width: 0px !important;
      background-color: transparent !important;
      .label {
        font-size: 1.2em;
        transform:translateY(3px);
      }
      .sublabel {
        font-size: 0.7em;
        opacity: 0.6;
        transform:translateY(-7px);
      }
    }
  }
</style>
