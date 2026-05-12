<template>
  <div id='newtab-wrapper' @dblclick='cycleLayout'>
    <div id='newtab' :class='{fullscreen}'>
      <Transition name='layout-fade' mode='out-in'>
        <div v-if='layout === "simple"' id='simple' key='simple' >
          <LogoWidget :fullscreen='fullscreen'/>
          <TimeWidget :fullscreen='fullscreen'/>
          <NewsWidget :fullscreen='fullscreen'/>
        </div>
        <div v-else-if='layout === "stats"' id='stats' key='stats'>
          <div class='grid-layout'>
            <div class='stats-col col-1'>
              <TimeWidget :fullscreen='fullscreen' compact class='widget'/>
              <CpuWidget :animationDuration='chartAnimationDuration' :animationStyle='chartAnimationStyle'/>
              <NvidiaWidget :animationDuration='chartAnimationDuration' :animationStyle='chartAnimationStyle'/>
            </div>
            <div class='stats-col col-2'>
              <NetworkWidget :animationDuration='chartAnimationDuration' :animationStyle='chartAnimationStyle'/>
              <ProcessesWidget/>
            </div>
            <div class='stats-col col-3'>
              <MemoryWidget/>
              <FilesystemWidget/>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import useStorage from '@/composables/useStorage'
  import useGlances from '@/composables/useGlances'
  import LogoWidget from './LogoWidget.vue'
  import NewsWidget from './NewsWidget.vue'
  import TimeWidget from './TimeWidget.vue'
  import CpuWidget from './StatsCpuWidget.vue'
  import MemoryWidget from './StatsMemoryWidget.vue'
  import NvidiaWidget from './StatsNvidiaWidget.vue'
  import ProcessesWidget from './StatsProcsWidget.vue'
  import NetworkWidget from './StatsNetworkWidget.vue'
  import FilesystemWidget from './StatsFilesystemWidget.vue'

  const {start} = useGlances()
  const layouts = ['simple', 'stats']
  const layout = useStorage('newtab.layout', 'simple')  // Current active layout
  const chartAnimationDuration = 2000                   // Chart scroll animation duration in ms
  const chartAnimationStyle = 'linear'                  // Chart scroll animation style: 'ease' or 'linear'
  const fullscreen = ref(false)                         // True when browser is in fullscreen

  // On Mounted
  // Initialize fullscreen status and update on resize
  onMounted(function() {
    start()
    updateFullscreen()
    window.addEventListener('resize', updateFullscreen)
  })

  // Cycle Layout
  // Advance to the next layout in the list
  const cycleLayout = function() {
    const next = (layouts.indexOf(layout.value) + 1) % layouts.length
    layout.value = layouts[next]
  }

  // Update Fullscreen
  // Update the 'fullscreen' ref to true if browser is in fullscreen
  const updateFullscreen = async function() {
    fullscreen.value = ((Math.abs(window.innerWidth - window.outerWidth) <= 5)
     && (Math.abs(window.innerHeight - window.outerHeight) <= 5))
  }
</script>

<style>
  #newtab-wrapper {
    background: black;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    position: relative;
    cursor: default;
    user-select: none;
    display: flex;
  }

  #newtab {
    background-size: cover;
    background: url('/static/img/floral-pattern.jpg') no-repeat center center / cover;
    color: var(--darkbg-fg4);
    font-family: var(--fontfamily-title);
    font-weight: 400;
    text-shadow: 1px 1px 10px #000;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw; height: 100vh;
    a, a:visited {
      color: inherit;
      text-decoration: none;
      &:hover { text-decoration: underline; }
    }
    &.fullscreen {
      width: calc(100vw - 20px); height: calc(100vh - 20px);
      animation: square-move 240s linear infinite;
    }
  }

  /* ------------------------------
  /* Simple Layout
  /* ---------------------------- */
  #simple {
    position: relative;
    width:100%; height:100%;
  }

  /* ------------------------------
  /* Stats Layout
  /* ---------------------------- */
  #stats {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width:1900px; height:1060px;
    border: 1px solid #fff2;
    border-radius: 12px;
    font-size: 16px;

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
  .fullscreen #stats {
    border-width: 0px;
  }
  
  /* ------------------------------
  /* Animations
  /* ---------------------------- */
  .layout-fade-enter-active, .layout-fade-leave-active { transition: opacity 0.5s ease; }
  .layout-fade-enter-from, .layout-fade-leave-to { opacity: 0; }

  @keyframes square-move {
    0% { transform: translate(0, 0); }
    25% { transform: translate(20px, 0); }
    50% { transform: translate(20px, 20px); }
    75% { transform: translate(0, 20px); }
    100% { transform: translate(0, 0); }
  }
</style>
