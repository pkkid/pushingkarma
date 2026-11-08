<template>
  <div id='x11pygrid'>
    <p class='lede'>
      Hold Ctrl+Alt and tap the numpad to throw the focused window into a slot on the
      grid. Tap the same key again to cycle through widths. Try it below.
    </p>
    <div class='demo'>
      <div class='desktop' ref='desktop'>
        <div class='window' :style='windowStyle'>
          <div class='titlebar'><i/><i/><i/></div>
          <div class='line'/><div class='line' style='width:60%'/><div class='line' style='width:75%'/>
        </div>
        <div class='taskbar'/>
      </div>
      <div class='numpad'>
        <button v-for='key in KEYS' :key='key' type='button' :class='{active:key == current}'
          :aria-label='`Numpad ${key}`' @click='snap(key)'>{{key}}</button>
        <div class='label'>Ctrl + Alt +<br/>Numpad</div>
      </div>
    </div>
    <div class='caption'>Tap a key twice to cycle 1/2, 1/3 and 2/3 widths, like the real thing.</div>
    <h2>Getting started</h2>
    <pre><span class='comment'># Needs python3-gi and python3-xlib</span>
pip install x11pygrid
x11pygrid  <span class='comment'># runs in the background, then use Ctrl+Alt+Numpad</span></pre>
  </div>
</template>

<script setup>
  import {computed, ref} from 'vue'

  defineProps({project:{type:Object, required:true}})
  const KEYS = [7, 8, 9, 4, 5, 6, 1, 2, 3]  // Numpad layout, top row first
  const TASKBAR = 0.06                      // Fraction of the desktop height used by the taskbar
  const current = ref(5)                    // Last numpad key pressed
  const cycle = ref(0)                      // Width cycle position for repeated presses

  // Window Style
  // Position the window for the current key and width cycle. Columns 1 and 3 cycle
  // 1/2, 1/3, 2/3 widths; the middle column cycles full, 1/3, 2/3. Rows map to the
  // top half, full height and bottom half of the screen.
  const windowStyle = computed(function() {
    var col = (current.value - 1) % 3
    var row = Math.floor((current.value - 1) / 3)
    var width = (col == 1 ? [1, 1/3, 2/3] : [1/2, 1/3, 2/3])[cycle.value]
    var left = col == 0 ? 0 : col == 2 ? 1 - width : (1 - width) / 2
    var usable = 1 - TASKBAR
    var top = row == 0 ? usable / 2 : 0
    var height = row == 1 ? usable : usable / 2
    return {left:`${left * 100}%`, width:`${width * 100}%`, top:`${top * 100}%`, height:`${height * 100}%`}
  })

  // Snap
  // Move the window to the slot for the key, cycling widths on repeated presses
  function snap(key) {
    cycle.value = key == current.value ? (cycle.value + 1) % 3 : 0
    current.value = key
  }
</script>

<style>
  #x11pygrid {
    .demo {
      background-color: var(--darkbg-bgh);
      border-radius: 12px;
      display: grid;
      gap: 18px;
      grid-template-columns: 1fr 156px;
      margin: 10px 0px 8px 0px;
      padding: 18px;
    }
    .desktop {
      aspect-ratio: 16 / 10;
      background: #32302f url('/static/img/backgrounds/china-2007-landscape.png') center / cover;
      border-radius: 6px;
      overflow: hidden;
      position: relative;
    }
    .taskbar {
      background-color: #1d2021d9;
      bottom: 0px;
      height: 6%;
      left: 0px;
      position: absolute;
      right: 0px;
    }
    .window {
      background-color: #fbf1c7;
      border: 1px solid #0003;
      border-radius: 5px;
      box-shadow: 0 10px 30px #0007;
      overflow: hidden;
      position: absolute;
      transition: all .28s cubic-bezier(.2,.8,.2,1);
      .titlebar {
        align-items: center;
        background-color: #504945;
        display: flex;
        gap: 4px;
        height: 16px;
        padding: 0px 6px;
        i { background-color:#a89984; border-radius:50%; height:6px; width:6px; }
      }
      .line { background-color:#e1d6b5; border-radius:3px; height:5px; margin:8px 10px 0px 10px; }
    }
    .numpad {
      align-content: start;
      display: grid;
      gap: 6px;
      grid-template-columns: repeat(3, 1fr);
      button {
        aspect-ratio: 1;
        background-color: #3c3836;
        border: 0px;
        border-radius: 7px;
        box-shadow: 0 3px 0 #1d2021;
        color: var(--darkbg-fg1);
        cursor: pointer;
        font-family: var(--fontfamily-code);
        font-size: 17px;
        &:hover { background-color:#504945; }
        &.active { background-color:#fe8019; box-shadow:0 1px 0 #1d2021; color:#1d2021; transform:translateY(2px); }
      }
      .label {
        color: var(--darkbg-fg3);
        font-family: var(--fontfamily-code);
        font-size: 11px;
        grid-column: 1 / -1;
        line-height: 1.5;
        margin-top: 6px;
        text-align: center;
      }
    }
    .caption { color:var(--lightbg-fg4); font-size:12.5px; margin-bottom:10px; }
  }

  @media (max-width: 700px) {
    #x11pygrid .demo { grid-template-columns:1fr; }
  }
</style>
