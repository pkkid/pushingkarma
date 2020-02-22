<template>
  <div id='clock'>
    <div v-if='now' class='date'>{{now | formatDate('dddd, MMM DD, YYYY') }}</div>
    <div v-if='now' class='time'>{{now | formatDate('h:mma') }}</div>
  </div>
</template>

<script>
  export default {
    name: 'NewTabClock',
    data: () => ({now: new Date()}),
    mounted: function() {
      setInterval(() => this.now = new Date(), 10000);
    },
  };
</script>

<style lang='scss'>
 #clock {
    background-color: $newtab_highlight;
    left: calc(50% - 150px);
    position: absolute;
    text-align: center;
    top: 20px;
    width: 300px;
    //opacity: 0;
    //transition: $newtab_transition_slow;
    //cursor: pointer;
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
