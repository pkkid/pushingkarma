<template>
  <Transition name='fade' style='transition-duration:1s;' appear>
    <div class='iconmessage'>
      <template v-if='!icon' />
      <i v-else-if='icon.startsWith("mdi")' class='mdi' :class='`${icon} ${animation}`'/>
      <div v-else class='iconimg' :class='animation' />
      <div class='text' v-if='text'>{{text}}
        <span v-if='ellipsis' class='ellipsis'>
          <span class='dot1'>.</span>
          <span class='dot2'>.</span>
          <span class='dot3'>.</span>
        </span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
  import {computed} from 'vue'

  const props = defineProps({
    // Container properties
    width: {type:String, default:'100%'},                     // Width of surrounding div
    height: {type:String, default:'150px'},                   // Height of surrounding div
    color: {type:String, default:'var(--lightbg-fg3)'},       // Color of the icon and text
    // Icon properties
    icon: {type:String, default:null},                        // Icon to use; mdi-icon-name or url(...)
    iconsize: {type:String, default:'30px'},                  // Icon width & height
    animation: {type:String, default:''},                     // Icon animation {gelatine, pulse, fade}
    // Text properties
    text: {type:String, default:null},                        // Text to display below icon
    textsize: {type:String, default:'12px'},                  // Text font-size
    ellipsis: {type:Boolean, default:false},                  // Text animated ellipsis (boolean)
  })

  // Shorthand for pk logo image
  const _icon = computed(() => props.icon == 'pk' ? 'url(/static/img/pk.svg)' : props.icon)
</script>

<style>
  .iconmessage {
    align-items: center;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    height: v-bind(height);
    justify-content: center;
    width: v-bind(width);

    .iconimg, .mdi {
      height: v-bind(iconsize);
      width: v-bind(iconsize);
      font-size: v-bind(iconsize);
      color: v-bind(color);
      &.gelatine { animation: loading-gelatine 1.5s infinite; }
      &.pulse { animation: loading-pulse 1s infinite ease-in-out alternate; }
      &.fade { animation: loading-fade 2s linear infinite; }
    }
    .iconimg {
      background-color: v-bind(color);
      mask: v-bind(_icon) no-repeat center / contain;
    }
    .text {
      color: v-bind(color);
      font-family: var(--fontfamily-title);
      font-size: v-bind(textsize);
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
