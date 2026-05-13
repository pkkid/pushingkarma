<template>
  <div id='stats'>
    <div class='grid-layout'>
      <div class='stats-col col-1'>
        <TimeWidget compact class='widget'/>
        <CpuWidget />
        <!-- <NvidiaWidget /> -->
      </div>
      <div class='stats-col col-2'>
        <!-- <NetworkWidget />
        <ProcessesWidget/> -->
      </div>
      <div class='stats-col col-3'>
        <!-- <MemoryWidget/>
        <FilesystemWidget/> -->
      </div>
    </div>
  </div>
</template>

<script setup>
  import {onMounted} from 'vue'
  import {useStorage} from '@/composables'
  import useGlances from '@/composables/useGlances'
  import TimeWidget from './TimeWidget.vue'
  import CpuWidget from './StatsCpuWidget.vue'
  import MemoryWidget from './StatsMemoryWidget.vue'
  import NvidiaWidget from './StatsNvidiaWidget.vue'
  import ProcessesWidget from './StatsProcsWidget.vue'
  import NetworkWidget from './StatsNetworkWidget.vue'
  import FilesystemWidget from './StatsFilesystemWidget.vue'

  const {startGlances} = useGlances()
  const host = useStorage('newtab.glances.host', 'http://192.168.4.253:61208')
  
  onMounted(function() {
    startGlances(host.value)
  })
</script>

<style>
  #stats {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1900px; height: 1060px;
    border: 1px solid #fff2;
    border-radius: 12px;
    font-size: 16px;

    &.fullscreen { border-width: 0px; }

    .grid-layout {
      display: grid;
      grid-template-columns: 33% 33% 33%;
      grid-template-rows: 100%;
      gap: 12px;
      padding: 20px;
      width: 1900px;
      height: 1060px;
      box-sizing: border-box;
      font-size: 30px;
      .stats-col {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
    }

    /* Widgets */
    .widget {
      background: #0006;
      border-radius: 8px;
      padding: 25px 15px;
      overflow: hidden;
      font-size: 28px;
      .header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        .title {
          font-size: 0.8em;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          opacity: 0.6;
          font-weight: bold;
        }
        .values {
          font-size: 1.2em;
          font-weight: 500;
          font-weight: bold;
          span { opacity: 0.6; }
        }
      }

      /* Metrics */
      .metrics .name {
        margin-right: 10px;
        opacity: 0.6;
      }

      /* Charts */
      .chartrow {
        display: grid;
        gap: 5px;
        grid-template-columns: 1fr;
        grid-template-rows: 150px;
        margin-bottom: 10px;
        .chartwrap { margin-bottom: 0px; }
      }
      .chartwrap {
        background-color: #0005;
        border-radius: 6px;
        border: 1px solid #3339;
        margin-bottom: 10px;
        overflow: hidden;
        position: relative;
        width: 100%;
        .maxvalue {
          position: absolute;
          top: 5px;
          left: 5px;
          font-size: 0.6em;
          font-weight: bold;
          opacity: 0.5;
        }
      }
    }
  }
</style>
