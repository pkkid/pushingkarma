<template>
  <div id='photo' v-if='loaded'>
    <div class='title'><span v-if='photo.title'>{{photo.title}} |</span> {{photo.user}}</div>
    <span class='mdi mdi-autorenew'></span>
    <div class='description'>{{photo.description}}</div>
  </div>
</template>

<script>
  import * as api from '@/api';

  export default {
    name: 'NewTabPhoto',
    data: () => ({
      loaded: false,
      photo: null,
    }),
    mounted: async function() {
      var {data} = await api.Tools.getPhoto();
      this.photo = data;
      this.loaded = true;
    },
  };
</script>

<style lang='scss'>
  #photo {
    background-color: $newtab_highlight;
    color: $newtab_dim;
    display: table;
    margin: 0 auto;
    font-size: 12px;
    opacity: 1;
    position: relative;
    top: 130px;
    transition: $newtab_transition_fast;
    max-width: 600px;
    background-color: rgba(0,0,0,0.6);
    border-radius: 4px;
    padding: 10px;
    .mdi-autorenew {
      font-size: 16px;
      position: relative;
      top: -2px;
      cursor: pointer;
      display: block;
      float: left;
    }
    .title { font-size:14px; float:left; padding-right:5px; }
    .description { clear:left; }
    &.hidedetails { opacity: 0; }
  }
</style>
