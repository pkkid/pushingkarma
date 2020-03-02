<template>
  <transition name='custom-classes-transition' enter-active-class='animated fadeIn'>
    <div id='clock' v-if='loaded'>
      <div v-if='now' class='date'>{{now | formatDate('dddd, MMM DD, YYYY') }}</div>
      <div v-if='now' class='time'>{{now | formatDate('h:mma') }}</div>
    </div>
  </transition>
</template>

<script>
  export default {
    name: 'NewTabClock',
    data: () => ({
      loaded: false,
      now: new Date()
    }),
    mounted: function() {
      setInterval(() => this.now = new Date(), 10000);
      setTimeout(() => this.loaded = true, 300);
    },
  };
</script>

<style lang='scss'>
 #clock {
    left: calc(50% - 150px);
    position: absolute;
    text-align: center;
    top: 20px;
    width: 300px;
    transition: $newtab_transition_slow;
    cursor: pointer;
    .date {
      color: $newtab_dim;
      font-size: 23px;
      margin-bottom: -15px;
    }
    .time {
      font-size: 60px;
    }
  }
</style>
