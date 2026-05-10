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
          <div class='wrapper'>
            <div class='hello'>Hello World</div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import useStorage from '@/composables/useStorage'
  import LogoWidget from './LogoWidget.vue'
  import NewsWidget from './NewsWidget.vue'
  import TimeWidget from './TimeWidget.vue'

  const layouts = ['simple', 'stats']
  const layout = useStorage('newtab.layout', 'simple')   // Current active layout
  const fullscreen = ref(false)   // True when browser is in fullscreen

  // On Mounted
  // Initialize fullscreen status and update on resize
  onMounted(function() {
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
  }

  #newtab {
    background-size: cover;
    background: url('/static/img/floral-pattern.jpg') no-repeat center center / cover;
    color: var(--darkbg-fg4);
    font-family: var(--fontfamily-title);
    font-weight: 400;
    text-shadow: 1px 1px 10px #000;
    position: relative;
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

  /* Simple Layout */
  #simple {
    position: relative;
    width:100%; height:100%;
  }

  /* Stats Layout */
  #stats {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width:100%; height:100%;
    .wrapper {
      width:1900px; height:1060px;
      border: 1px solid #eee4;
    }
  }
  #stats {
    display: flex;
    align-items: center;
    justify-content: center;
    .hello { font-size: 4rem; }
  }

  /* Animations */
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
