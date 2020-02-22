<template>
  <div id='news'>
    <div class='title'><p style='-webkit-box-orient:vertical'>
      <a target='_blank' href='{article.url}'>{article.title}</a>
    </p></div>
    <div class='subtext'>
      {timeAgo article.created_utc} |
      <a target='_blank' href='{article.redditurl}'>{article.subreddit}</a> |
      <a target='_blank' href='https://{article.domain}'>{article.domain}</a>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NewTabNews',
  };
</script>

<style lang='scss'>
</style>
