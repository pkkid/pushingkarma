<template>
  <div id='newtab-wrapper'>
    <div id='newtab' :class='{fullscreen}'>
      <div class='logoimg'/>
      <div class='time-container'>
        <div class='time'>{{utils.formatDate(now, 'h:mm')}}</div>
        <div class='date'>{{utils.formatDate(now, 'MMMM D, YYYY')}}</div>
      </div>
      <Transition name='fade' style='transition-duration:1s;'>
        <div class='news-container' v-if='news && shownews'>
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
    </div>
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const now = ref()                 // Current datetime
  const news = ref(null)            // List of Reddit news posts to cycle
  const newsindex = ref(0)          // Current index in news posts
  const shownews = ref(true)     // True when news post is showing
  const fullscreen = ref(false)     // True when browser is in fullscreen
  const reddit_queries = [
    // {subreddit:'news', count:15, maxtitle:150, maxtext:100},
    // {subreddit:'technology', count:15, maxtitle:150, maxtext:100},
    // {subreddit:'worldnews', count:15, maxtitle:150, maxtext:100},
    // {subreddit:'boston', count:10, maxtitle:150, maxtext:100},
    {subreddit:'jokes', count:15, maxtitle:150, mintext:5, maxtext:100},
    {subreddit:'dadjokes', count:15, maxtitle:150, mintext:5, maxtext:100},
  ]
  
  // On Mounted
  // Initialize date and fullscreen status, set interval to update
  // date every second
  onMounted(function() {
    updateTime()
    updateFullscreen()
    updateNews()
    setInterval(updateTime, 1000)  // 1s
    setInterval(updateNews, 900000)  // 15m
    setInterval(showNextNewsPost, 60000)  // 60s
    window.addEventListener('resize', updateFullscreen)
    hotkeys('left', 'newtab', function() { showNextNewsPost(-1) })
    hotkeys('right', 'newtab', function() { showNextNewsPost() })
    hotkeys.setScope('newtab')
  })

  // Update Fullscreen
  // Update the 'fullscreen' ref to true if browser is in fullscreen
  const updateFullscreen = async function() {
    fullscreen.value = ((Math.abs(window.innerWidth - window.outerWidth) <= 5)
     && (Math.abs(window.innerHeight - window.outerHeight) <= 5))
  }

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

  // Update Time
  // Update the 'now' ref to current datetime
  const updateTime = async function() {
    now.value = new Date()
  }
</script>

<style>
  #newtab-wrapper {
    background: black;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    position: relative;
  }

  #newtab {
    background-size: cover;
    background: url('/static/img/floral-pattern.jpg') no-repeat center center / cover;
    color: var(--darkbg-fg4);
    font-family: var(--fontfamily-title);
    font-weight: 400;
    text-shadow: 1px 1px 10px #000;
    position: relative;
    width: 100vw; height: 100vh;

    a, a:visited {
      color: inherit;
      text-decoration: none;
      &:hover { text-decoration: underline; }
    }

    .logoimg {
      aspect-ratio: 1/1;
      background-color: color-mix(in srgb, var(--darkbg-fg1), #000 20%);
      mask: url('/static/img/pk.svg') no-repeat center/contain;
      position: absolute;
      top: 20px; left: 20px;
      width: 80px;
    }

    .time-container {
      position: absolute;
      top: 45%; left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      .time { font-size:8rem; }
      .date { font-size:3rem; margin-top:-40px; }
    }

    .news-container {
      position: absolute;
      bottom: 0%; left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      font-size: 1.5rem;
      width: 90vw;
      .title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .subtext { margin-top:2px }
    }

    &.fullscreen {
      width: calc(100vw - 20px); height: calc(100vh - 20px);
      animation: square-move 240s linear infinite;
      .logoimg { width:100px; top:40px; left:40px; }
      .time-container .time { font-size:12rem; }
      .time-container .date { font-size:4rem; }
      .news-container { font-size: 2.8rem; }
    }

  }

  @keyframes square-move {
    0% { transform: translate(0, 0); }
    25% { transform: translate(20px, 0); }
    50% { transform: translate(20px, 20px); }
    75% { transform: translate(0, 20px); }
    100% { transform: translate(0, 0); }
  }
</style>
