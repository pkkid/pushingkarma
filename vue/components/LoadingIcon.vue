<template>
  <Transition name='fade' style='transition-duration:1s;' appear>
    <div class='loadingicon-wrap'>
      <div class='loadingicon' :class='animation' />
    </div>
  </Transition>
</template>

<script setup>
  const props = defineProps({
    icon: {type:String, default:'url(/static/img/pk.svg)'},
    width: {type:String, default:'100%'},
    height: {type:String, default:'auto'},
    size: {type:String, default:'30px'},
    fill: {type:String, default:'#928374'},
    animation: {type:String, default:'gelatine'},
  })
</script>

<style>
  .loadingicon-wrap {
    width: v-bind(width);
    height: v-bind(height);
    display: flex;
    justify-content: center;
    align-items: center;

    .loadingicon {
      align-items: center;
      background-color: v-bind(fill);
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
</style>
