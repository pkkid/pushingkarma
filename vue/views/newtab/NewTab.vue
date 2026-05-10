<template>
  <div id='newtab-wrapper'>
    <div id='newtab' :class='{fullscreen}'>
      <Transition name='layout-fade' mode='out-in'>
        <div v-if='layout === "simple-layout"' class='simple-layout' key='simple-layout' @dblclick.self='cycleLayout'>
          <LogoWidget :fullscreen='fullscreen'/>
          <TimeWidget :fullscreen='fullscreen'/>
          <NewsWidget :fullscreen='fullscreen'/>
        </div>
        <div v-else-if='layout === "stats-layout"' class='stats-layout' key='stats-layout' @dblclick.self='cycleLayout'>
          <div class='hello'>Hello World</div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import LogoWidget from './LogoWidget.vue'
  import NewsWidget from './NewsWidget.vue'
  import TimeWidget from './TimeWidget.vue'

  const layouts = ['simple-layout', 'stats-layout']
  const layout = ref('simple-layout')   // Current active layout
  const fullscreen = ref(false)         // True when browser is in fullscreen

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

  .simple-layout, .stats-layout {
    width: 100%; height: 100%;
    position: relative;
  }

  .stats-layout {
    display: flex;
    align-items: center;
    justify-content: center;
    .hello { font-size: 4rem; }
  }

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
