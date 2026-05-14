<template>
  <div id='stats'>
    <div class='grid-layout'>
      <div class='stats-col col-1'>
        <WidgetTime compact class='widget'/>
        <WidgetCpu />
        <WidgetNvidia />
      </div>
      <div class='stats-col col-2'>
        <WidgetMemory />
        <WidgetNetwork />
      </div>
      <div class='stats-col col-3'>
        <WidgetFilesystem />
        <WidgetProcs />
      </div>
    </div>
  </div>
</template>

<script setup>
  import {onMounted} from 'vue'
  import {useStorage} from '@/composables'
  import useGlances from '@/composables/useGlances'
  import WidgetTime from './WidgetTime.vue'
  import WidgetCpu from './WidgetCpu.vue'
  import WidgetMemory from './WidgetMemory.vue'
  import WidgetNvidia from './WidgetNvidia.vue'
  import WidgetProcs from './WidgetProcs.vue'
  import WidgetNetwork from './WidgetNetwork.vue'
  import WidgetFilesystem from './WidgetFilesystem.vue'

  const {startGlances} = useGlances()
  const host = useStorage('newtab.stats.host', 'http://192.168.4.253:61208')
  
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
      --gap: 20px;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      grid-template-rows: 100%;
      gap: var(--gap);
      padding: 20px;
      width: 1900px;
      height: 1060px;
      box-sizing: border-box;
      font-size: 30px;
      .stats-col {
        display: flex;
        flex-direction: column;
        gap: var(--gap);
      }
    }

    /* Widgets */
    .widget {
      background: #0006;
      border-radius: 8px;
      padding: 25px 15px;
      overflow: hidden;
      font-size: 28px;
      .header {
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
        }
      }
      .delim { opacity:0.4; margin:0px 10px; }
      .delimtext { opacity: 0.8; }

      /* Metrics */
      .metrics {
        font-size: 0.9em;
        &.twocols {
          column-gap: 50px;
          display: grid;
          grid-template-columns: auto auto;
          justify-content: start;
        }
        label {
          display: inline;
          font-size: 1em;
          margin-right: 5px;
          opacity: 0.7;
        }
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
          top: 1px;
          left: 5px;
          font-size: 0.6em;
          font-weight: bold;
          opacity: 0.5;
        }
      }
    }
  }
</style>
