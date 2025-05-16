<template>
  <Transition name='fade' style='transition-duration:1s;' appear>
    <div class='loadingicon-wrap'>
      <div class='loadingicon' :class='animation' />
      <div class='text' v-if='text'>{{text}}
        <span class='ellipsis'>
          <span class='dot1'>.</span>
          <span class='dot2'>.</span>
          <span class='dot3'>.</span>
        </span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
  const props = defineProps({
    animation: {type:String, default:'gelatine'},             // Image animation to use
    color: {type:String, default:'var(--lightbg-fg3)'},       // Color of the icon and text
    fontsize: {type:String, default:'12px'},                  // Font size of the text
    height: {type:String, default:'auto'},                    // Height of surrounding div
    icon: {type:String, default:'url(/static/img/pk.svg)'},   // Icon to use
    size: {type:String, default:'30px'},                      // Width & height of icon
    text: {type:String, default:null},                        // Text to display below icon  
    width: {type:String, default:'100%'},                     // Width of surrounding div
  })
</script>

<style>
  .loadingicon-wrap {
    width: v-bind(width);
    height: v-bind(height);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

    .loadingicon {
      align-items: center;
      background-color: v-bind(color);
      display: flex;
      height: v-bind(size);
      aspect-ratio: 1;
      justify-content: center;
      mask: v-bind(icon) no-repeat center / contain;
      width: v-bind(size);
      &.gelatine { animation: loading-gelatine 1.5s infinite; }
      &.pulse { animation: loading-pulse 1s infinite ease-in-out alternate; }
      &.fade { animation: loading-fade 2s linear infinite; }
    }
    .text {
      color: v-bind(color);
      font-family: var(--fontfamily-title);
      font-size: v-bind(fontsize);
      margin-top: 0.3em;
      opacity: 0.85;
      .ellipsis {
        display: inline-block;
        margin-left: 0.2em;
        .dot1, .dot2, .dot3 { opacity:0; animation: ellipsis 1.2s infinite; }
        .dot1 { animation-delay: 0s; }
        .dot2 { animation-delay: 0.3s; }
        .dot3 { animation-delay: 0.6s; }
      }
    }
  }
  
  @keyframes loading-gelatine {
    from, to { transform: scale(1, 1); }
    10% { transform: scale(0.9, 1.1); }
    20% { transform: scale(1.1, 0.9); }
    30% { transform: scale(0.95, 1.05); }
    40% { transform: scale(1, 1); }
    100% { transform: scale(1, 1); }
  }
  @keyframes loading-pulse {
    from { transform: scale(0.8); }
    to { transform: scale(1.1); }
  }
  @keyframes loading-fade {
    from, to { opacity: 0.2; }
    50% { opacity: 1; }
  }

  @keyframes ellipsis {
    0%, 19%   { opacity: 0; }
    20%, 100% { opacity: 1; }
    85%, 100% { opacity: 0; }
  }
</style>
