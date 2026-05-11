<template>
  <Transition name='fade' style='transition-duration:1s;'>
    <div id='newswidget' :class='{fullscreen}' v-if='news && shownews'>
      <div class='title'>
        <a target='_blank' :href='news[newsindex].url'>{{news[newsindex].title}}</a>
      </div>
      <div v-if='news[newsindex].selftext' class='subtext'>
        {{news[newsindex].selftext}} | {{utils.intComma(news[newsindex].score)}} upvotes
      </div>
      <div v-else class='subtext'>
        {{ utils.timeAgo(new Date(news[newsindex].created)) }} |
        <a target='_blank' :href='news[newsindex].redditurl'>{{news[newsindex].subreddit}}</a> |
        {{utils.intComma(news[newsindex].score)}} upvotes
      </div>
    </div>
  </Transition>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
  })
  const news = ref(null)                          // List of news posts
  const newsindex = ref(0)                        // Index of the currently displayed news post
  const shownews = ref(true)                      // Show the news post (used for fade transition)
  const reddit_queries = [
    {subreddit:'news', count:15, maxtitle:150, maxtext:100},
    {subreddit:'technology', count:15, maxtitle:150, maxtext:100},
    {subreddit:'technews', count:15, maxtitle:150, maxtext:100},
    {subreddit:'worldnews', count:15, maxtitle:150, maxtext:100},
    {subreddit:'upliftingnews', count:15, maxtitle:150, maxtext:100},
    {subreddit:'positive_news', count:15, maxtitle:150, maxtext:100},
    {subreddit:'hackernews', count:15, maxtitle:150, maxtext:100},
    {subreddit:'nottheonion', count:15, maxtitle:150, maxtext:100},
    {subreddit:'goodnews', count:15, maxtitle:150, maxtext:100},
    {subreddit:'boston', count:10, maxtitle:150, maxtext:100},
    {subreddit:'jokes', count:15, maxtitle:150, mintext:5, maxtext:100},
    {subreddit:'dadjokes', count:15, maxtitle:150, mintext:5, maxtext:100},
  ]

  // Update Reddit
  // Fetch posts from specified subreddits and store them in localStorage
  const updateNews = async function() {
    var data = await api.Reddit.getNews({queries:reddit_queries})
    news.value = data.data.posts.sort(() => Math.random() - 0.5)
    newsindex.value = Math.floor(Math.random() * news.value.length)
    console.log(news.value)
  }

  // Show Next Reddit Post
  // Display the next Reddit post from localStorage
  const showNextNewsPost = async function(offset=1) {
    if (news.value) {
      shownews.value = false
      await utils.sleep(500)
      newsindex.value = (newsindex.value + offset) % news.value.length
      await utils.sleep(500)
      shownews.value = true
    }
  }

  // On Mounted
  // Initialize news and set intervals for updates
  onMounted(function() {
    updateNews()
    setInterval(updateNews, 900000)   // 15m
    setInterval(showNextNewsPost, 60000)  // 60s
    hotkeys('left', 'newtab', function() { showNextNewsPost(-1) })
    hotkeys('right', 'newtab', function() { showNextNewsPost() })
    hotkeys.setScope('newtab')
  })
</script>

<style>
  #newswidget {
    position: absolute;
    bottom: 0%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    font-size: 1.5rem;
    width: 90vw;
    .title {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .subtext { margin-top:2px }
    &.fullscreen { font-size:2.8rem; }
  }
</style>
