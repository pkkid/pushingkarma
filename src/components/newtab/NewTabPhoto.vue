<template>
  <div id='photo' :class='{showdetails}'>
    <div class='bgimg' :style='{backgroundImage:bgimage, opacity:bgopacity}'/>
    <div class='details' v-if='photo'>
      <div class='title'><span v-if='photo.title'>{{photo.title}} |</span> {{photo.user}}</div>
      <div class='description'>
        {{photo.description}}
        <span v-if='!forced'> - <a @click.prevent='refreshPhoto'>New Photo</a></span>
      </div>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  var FORCE_IMAGE = {
    url: require('../../assets/img/darkbg.jpg'),
    title: 'Black Floral Wallpaper',
    description: 'Black Floral Wallpaper 1920x1080',
    user: 'Unknown',
  };

  export default {
    name: 'NewTabPhoto',
    computed: {
      bgimage: function() { return this.photo ? 'url("'+ this.photo.url +'")' : ''; },
    },
    data: () => ({
      bgopacity: 0,
      forced: false,
      photo: null,
      showdetails: false,
    }),
    mounted: async function() {
      if (FORCE_IMAGE !== null) {
        this.photo = FORCE_IMAGE;
        this.forced = true;
      } else {
        var {data} = await api.Tools.getPhoto();
        this.photo = data;
      }
      await utils.preloadImage(this.photo.url);
      this.bgopacity = 1;
    },
    methods: {
      refreshPhoto: async function() {
        if (FORCE_IMAGE !== null) {
          this.bgopacity = 0;
          await utils.sleep(500);
          var {data} = await api.Tools.refreshPhoto();
          this.photo = data;
          await utils.preloadImage(this.photo.url);
          this.bgopacity = 1;
        }
      },
      toggleDetails: function() {
        this.showdetails = !this.showdetails;
      },
    },
  };
</script>

<style lang='scss'>
   #photo {
    .bgimg {
      width: 100%;
      height: 100vh;
      opacity: 0;
      background-position: center center;
      background-size: cover;
      z-index: 0;
    }
    .details {
      background-color: rgba(0,0,0,0.3);
      border-radius: 4px;
      color: $newtab_dim;
      display: table;
      font-size: 12px;
      left: 50%;
      margin: 0 auto;
      max-width: 400px;
      opacity: 0;
      padding: 10px;
      position: absolute;
      top: 130px;
      transform: translateX(-50%);
      transition: $newtab_transition;
      .title {
        font-size:14px;
        float: left;
        padding-right: 5px;
        margin-bottom: 0px;
        color: $newtab_color;
        font-weight: 400;
      }
      .description { clear:left; }
    }
    &.showdetails .details {
      opacity: 1;
    }
  }
  @media screen and (max-width: 1100px) {
    #photo .details { opacity: 0 !important; }
  }
  @media screen and (max-width: 970px) {
    #photo { opacity: 0; }
  }
</style>
