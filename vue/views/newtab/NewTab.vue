<template>
  <div id='newtab-wrapper' @dblclick='cycleLayout'>
    <Transition name='bookmarks-fade' appear appear-active-class='bookmarks-appear-active'>
      <BookmarksBar v-if='showBookmarks'/>
    </Transition>
    <QuickSearch/>
    <BookmarkDelete v-if='user'/>
    <div id='newtab' :class='{fullscreen, bookmarks:showBookmarks}'>
      <div class='wallpaper' :style='{backgroundImage:`url(${wallpaper})`}'/>
      <Transition name='wallpaper-fade' @after-enter='showNextWallpaper'>
        <div v-if='nextWallpaper' class='wallpaper' :style='{backgroundImage:`url(${nextWallpaper})`}'/>
      </Transition>
      <Transition name='layout-fade' mode='out-in'>
        <LayoutSimple v-if='activeLayout === "simple"' key='simple' />
        <LayoutStats v-else-if='activeLayout === "stats"' key='stats' :style='{zoom: statsZoom}' />
      </Transition>
    </div>
  </div>
</template>

<script setup>
  import {computed, inject, onMounted, onUnmounted, ref, watch} from 'vue'
  import useStorage from '@/composables/useStorage'
  import wallpaperUrl from '@/assets/img/floral-pattern.webp'
  import * as cache from './cache'
  import {tree} from './bookmarks'
  import BookmarkDelete from './BookmarkDelete.vue'
  import BookmarksBar from './BookmarksBar.vue'
  import QuickSearch from './QuickSearch.vue'
  import LayoutSimple from './LayoutSimple.vue'
  import LayoutStats from './LayoutStats.vue'

  const layouts = ['simple', 'stats']  // Two layout options
  const layout = useStorage('newtab.layout', 'simple')  // Current active layout
  const fullscreen = ref(false)  // True when browser is in fullscreen
  const statsZoom = ref(1)  // CSS zoom applied to stats layout when not fullscreen
  const {user} = inject('user')  // Current user, bookmarks require login
  const {globalvars} = inject('globalvars')  // Global variables, null until loaded from the server
  const wallpaper = ref(cache.get('newtab.wallpaper', wallpaperUrl))  // Wallpaper shown, cached from the last visit
  const nextWallpaper = ref(null)  // New wallpaper fading in over the cached one
  const loggedIn = computed(() => globalvars.value ? Boolean(user.value) : tree.value.length > 0)  // Assume cached bookmarks mean logged in until the user loads
  const activeLayout = computed(() => loggedIn.value ? layout.value : 'simple')  // Stats require login
  const showBookmarks = computed(() => !fullscreen.value && loggedIn.value)  // Bookmarks bar when windowed

  // Clear the cached bookmarks once the server says we are logged out
  watch(() => globalvars.value && !user.value, function(loggedOut) {
    if (loggedOut) { tree.value = [] }
  })

  // On Mounted / Unmounted
  // Initialize fullscreen status and update on resize. Add <base target='_top'> so links
  // open in the whole tab when this page is shown in a frame (the browser new tab
  // extension) instead of inside the frame. Outside a frame _top is the page itself.
  var base = null
  onMounted(function() {
    updateFullscreen()
    updateWallpaper()
    window.addEventListener('resize', updateFullscreen)
    base = document.createElement('base')
    base.target = '_top'
    document.head.appendChild(base)
  })
  onUnmounted(function() {
    window.removeEventListener('resize', updateFullscreen)
    base?.remove()
  })

  // Cycle Layout
  // Advance to the next layout in the list. The stats layout requires login, so
  // logged out users stay on the simple layout.
  const cycleLayout = function() {
    if (!user.value) { return }
    const next = (layouts.indexOf(layout.value) + 1) % layouts.length
    layout.value = layouts[next]
  }

  // Update Wallpaper
  // The cached wallpaper paints instantly (index.html paints it before the app loads).
  // When the site now uses a different one, load it in the background and fade it in.
  const updateWallpaper = function() {
    if (wallpaper.value === wallpaperUrl) { return cache.set('newtab.wallpaper', wallpaperUrl) }
    const img = new Image()
    img.onload = () => nextWallpaper.value = wallpaperUrl
    img.src = wallpaperUrl
  }
  const showNextWallpaper = function() {
    wallpaper.value = nextWallpaper.value
    nextWallpaper.value = null
    cache.set('newtab.wallpaper', wallpaper.value)
  }

  // Update Fullscreen
  // Update the 'fullscreen' ref to true if browser is in fullscreen
  // Also recompute statsZoom so stats layout fits with 200px margin when windowed
  const updateFullscreen = async function() {
    fullscreen.value = ((Math.abs(window.innerWidth - window.outerWidth) <= 5)
     && (Math.abs(window.innerHeight - window.outerHeight) <= 5))
    if (fullscreen.value) {
      statsZoom.value = 1
    } else {
      const statsW = 1900, statsH = 1060       // Natural size of the stats layout
      const marginX = 400, marginY = 200       // Total margin to preserve (sides x2, top/bottom x2)
      const maxWidth = 1100, minWidth = 800    // Clamp the effective rendered width
      const zoomX = (window.innerWidth - marginX) / statsW
      const zoomY = (window.innerHeight - marginY) / statsH
      statsZoom.value = Math.max(Math.min(zoomX, zoomY, maxWidth / statsW), minWidth / statsW)
    }
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
    flex-direction: column;
  }

  #newtab {
    isolation: isolate;
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
      /* steps(20) per 60s side: 1px jump every 3s, full 20px square every 240s (OLED burn-in) */
      animation: square-move 240s steps(20) infinite;
    }
  }

  #newtab .wallpaper {
    position: absolute;
    inset: 0;
    z-index: -1;
    background: no-repeat center center / cover;
  }

  /* ------------------------------
  /* Animations
  /* ---------------------------- */
  .layout-fade-enter-active, .layout-fade-leave-active { transition: opacity 0.5s ease; }
  .layout-fade-enter-from, .layout-fade-leave-to { opacity: 0; }
  .wallpaper-fade-enter-active, .wallpaper-fade-leave-active { transition: opacity 1s ease; }
  .wallpaper-fade-enter-from, .wallpaper-fade-leave-to { opacity: 0; }
  .bookmarks-fade-enter-active, .bookmarks-fade-leave-active { transition: opacity 0.3s ease; }
  .bookmarks-fade-enter-from, .bookmarks-fade-leave-to { opacity: 0; }
  .bookmarks-appear-active { transition: opacity 0.1s ease; }  /* Quick fade in on page load */
  #logowidget, #timewidget { animation: newtab-fade-in 0.1s ease; }  /* Same quick fade in */

  @keyframes newtab-fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes square-move {
    0% { transform: translate(0, 0); }
    25% { transform: translate(20px, 0); }
    50% { transform: translate(20px, 20px); }
    75% { transform: translate(0, 20px); }
    100% { transform: translate(0, 0); }
  }
</style>
