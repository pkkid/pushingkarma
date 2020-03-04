<template>
  <transition name='custom-classes-transition'
      enter-active-class='animated fadeIn'
      leave-active-class='animated fadeOut'>
    <div id='news' v-if='articles' :class='{showing}'>
      <div class='title'><p style='-webkit-box-orient:vertical'>
        <a target='_blank' :href='articles[index].url'>{{articles[index].title}}</a>
      </p></div>
      <div class='subtext'>
        {{ articles[index].created_utc | timeAgo }} ago |
        <a target='_blank' :href='articles[index].redditurl'>{{articles[index].subreddit}}</a> |
        <a target='_blank' :href='"https://"+ articles[index].domain'>{{articles[index].domain}}</a>
      </div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';

  export default {
    name: 'NewTabNews',
    data: () => ({
      articles: null,
      showing: true,
      index: 0,
    }),
    mounted: async function() {
      this.update();
      setInterval(this.update, 1000*60*5);
      setInterval(this.next, 1000*20);
    },
    methods: {
      update: async function() {
        var {data} = await api.Tools.getNews();
        this.articles = data;
        this.index = Math.floor(Math.random() * this.articles.length);
      },
      next: async function() {
        if (this.articles) {
          this.showing = false;
          await utils.sleep(500);
          this.index = (this.index + 1) % this.articles.length;
          await utils.sleep(200);
          this.showing = true;
        }
      },
    }
  };
</script>

<style lang='scss'>
  #news {
    bottom: 20px;
    left: 20px;
    max-height: 65px;
    position: absolute;
    width: 700px;
    opacity: 0;
    transition: opacity 0.5s linear;
    &.showing { opacity: 1; }
    .title p {
      display: -webkit-box;
      font-size: 20px;
      line-height: 22px;
      margin: 0px;
      max-height: 44px;
      overflow: hidden;
      -webkit-line-clamp: 2;
    }
    .subtext {
      font-size: 12px;
      color: $newtab_dim;
    }
  }
  @media screen and (max-width: 1100px) {
    #news { bottom:20px; left:20px; width:700px; }
  }
  @media screen and (max-width: 800px) {
    #news .subtext { color: $raspi_dim; }
  }
</style>
