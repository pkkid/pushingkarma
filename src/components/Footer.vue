<template>
  <div id='footer'>
    Copyright (c) 2019 PushingKarma. All rights reserved.
  </div>
</template>

<script>
  export default { name:'Footer' };
</script>

<style lang='scss'>
  @import '@/assets/css/main.scss';

  #footer {
    background-color: $darkbg-color;
    color: $darkbg-text;
    font-size: 13px;
    height: 150px;
    line-height: 150px;
    text-align: left;
  }
</style>
