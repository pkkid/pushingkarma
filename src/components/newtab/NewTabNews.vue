<template>
  <transition name='custom-classes-transition'
      enter-active-class='animated fadeIn'
      leae-active-class='animated fadeOut'>
    <div id='news' v-if='loaded'>
      <div class='title'><p style='-webkit-box-orient:vertical'>
        <a target='_blank' :href='article.url'>{{article.title}}</a>
      </p></div>
      <div class='subtext'>
        {{ article.created_utc | timeAgo }} |
        <a target='_blank' :href='article.redditurl'>{{article.subreddit}}</a> |
        <a target='_blank' :href='"https://"+ article.domain'>{{article.domain}}</a>
      </div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';

  export default {
    name: 'NewTabNews',
    data: () => ({
      loaded: false,
      articles: null,
      article: null,
    }),
    mounted: async function() {
      var {data} = await api.Tools.getNews();
      this.articles = data;
      this.article = this.articles[0];
      this.loaded = true;
    },
  };
</script>

<style lang='scss'>
  #news {
    background-color: $newtab_highlight;
    bottom: 20px;
    left: 20px;
    max-height: 65px;
    position: absolute;
    width: 700px;
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
</style>
