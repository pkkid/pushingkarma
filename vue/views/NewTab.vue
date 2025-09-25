<template>
  <div id='newtab-wrapper'>
    <div id='newtab' :class='{fullscreen}'>
      <div class='logo-container'>
        <div class='logoimg'/>
      </div>
      <div class='time-container'>
        <div class='time'>{{utils.formatDate(now, 'h:mm')}}</div>
        <div class='date'>{{utils.formatDate(now, 'MMMM D, YYYY')}}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {onMounted, onUnmounted, ref} from 'vue'
  import {utils} from '@/utils'

  var timeInterval = null           // Interval for datetime
  const now = ref()                 // Current datetime
  const fullscreen = ref(false)     // True when browser is in fullscreen
  const reddit_queries = [
    {subreddit:'news', count:15},
    {subreddit:'technology', count:15},
    {subreddit:'worldnews', count:15},
    {subreddit:'boston', count:10},
    {subreddit:'jokes', count:15, maxtitle:100, mintext:10, maxtext:200},
    {subreddit:'dadjokes', count:15, maxtitle:100, mintext:10, maxtext:200},
  ]
  
  // On Mounted
  // Initialize date and fullscreen status, set interval to update
  // date every second
  onMounted(function() {
    updateTime()
    updateFullscreen()
    timeInterval = setInterval(updateTime, 1000)
    window.addEventListener('resize', updateFullscreen)
  })

  // Update Time
  // Update the 'now' ref to current datetime
  const updateTime = function() {
    now.value = new Date()
  }

  // Update Fullscreen
  // Update the 'fullscreen' ref to true if browser is in fullscreen
  const updateFullscreen = function() {
    fullscreen.value = Math.abs(window.innerWidth - window.outerWidth) <= 5
  }

  // On Unmounted
  // Clear the time interval and remove the resize event listener
  onUnmounted(() => {
    if (timeInterval) { clearInterval(timeInterval) }
    window.removeEventListener('resize', updateFullscreen)
  })
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
    background: url('/static/img/floral-pattern.jpg') no-repeat center center fixed;
    background-size: cover;
    height: 100vh;
    width: 100vw;
    position: relative;
    &.fullscreen {
      height: calc(100vh - 20px);
      width: calc(100vw - 20px);
      animation: square-move 240s linear infinite;
    }

    .logo-container {
      align-items: center;
      display: flex;
      flex-direction: column;
      position: absolute;
      top: 30px; left: 30px;
      .logoimg {
        background-color: color-mix(in srgb, var(--darkbg-fg1), #000 20%);
        mask: url('/static/img/pk.svg') no-repeat center/contain;
        width: 100px; height: 100px;
      }
    }

    .time-container {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      .time {
        color: var(--darkbg-fg4);
        font-family: var(--fontfamily-title);
        font-size: 10rem;
        font-weight: 400;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
      }
      .date {
        color: var(--darkbg-fg4);
        font-family: var(--fontfamily-title);
        font-size: 3rem;
        font-weight: 400;
        margin-top: -40px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
      }
    }
  }

  @keyframes square-move {
    0% { transform: translate(0, 0); }
    25% { transform: translate(20px, 0); }
    50% { transform: translate(20px, 20px); }
    75% { transform: translate(0, 20px); }
    100% { transform: translate(0, 0); }
  }
</style>
