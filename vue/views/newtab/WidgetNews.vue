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
  import {onMounted, onUnmounted, ref} from 'vue'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const props = defineProps({
    fullscreen: {type: Boolean, default: false},  // True if browser fullscreen
  })
  const news = ref(null)                          // List of news posts
  const newsindex = ref(0)                        // Index of the currently displayed news post
  const shownews = ref(true)                      // Show the news post (used for fade transition)
  const intervals = []                            // Update and rotate intervals, cleared on unmount
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

  // Show Previous / Next
  // Hotkey handlers, named so they can be unbound on unmount
  const showPrevious = () => showNextNewsPost(-1)
  const showNext = () => showNextNewsPost()

  // On Mounted / Unmounted
  // Initialize news and set intervals for updates. Clear them, unbind the hotkeys
  // and drop the posts when switching layouts so nothing keeps running.
  onMounted(function() {
    updateNews()
    intervals.push(setInterval(updateNews, 900000))   // 15m
    intervals.push(setInterval(showNextNewsPost, 60000))  // 60s
    hotkeys('left', 'newtab', showPrevious)
    hotkeys('right', 'newtab', showNext)
    hotkeys.setScope('newtab')
  })
  onUnmounted(function() {
    intervals.forEach(clearInterval)
    hotkeys.unbind('left', 'newtab', showPrevious)
    hotkeys.unbind('right', 'newtab', showNext)
    news.value = null
  })
</script>

<style>
  #newswidget {
    position: absolute;
    bottom: 0%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    font-size: 1.7rem;
    width: 90vw;
    .title {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .subtext { margin-top:2px }
  }
  #newtab.fullscreen #newswidget {
    font-size:2.8rem;
  }
</style>
