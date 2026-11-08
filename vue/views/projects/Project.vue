<template>
  <div id='project' class='lightbg' v-if='project' :key='project.slug'>
    <!-- Banner header with name, GitHub stats and links -->
    <header class='banner'>
      <div class='bgimg' :class='{placeholder:!project.banner}' :style='bannerStyle(project)'/>
      <div class='shade'/>
      <div class='credit' v-if='project.banner && describe(project.banner)'>{{describe(project.banner)}}</div>
      <div class='inner'>
        <div class='title'>
          <h1>{{project.name}}</h1>
          <div class='tagline'>{{project.tagline}}</div>
          <div class='chips' v-if='github'>
            <span class='chip'><i class='mdi mdi-star' style='color:#fabd2f'/><b>{{utils.intComma(github.stars)}}</b> stars</span>
            <span class='chip'><i class='mdi mdi-source-fork'/><b>{{utils.intComma(github.forks)}}</b> forks</span>
            <span class='chip'><i class='mdi mdi-record-circle-outline'/><b>{{utils.intComma(github.issues)}}</b> open issues</span>
            <span class='chip' v-if='github.language'><span class='dot' :style='{backgroundColor:languageColor}'/>{{github.language}}</span>
            <span class='chip' v-if='recentlyUpdated'><i class='mdi mdi-clock-outline'/>Updated {{utils.timeAgo(new Date(github.pushed).getTime())}}</span>
          </div>
        </div>
        <div class='actions'>
          <a v-if='website' class='btn primary' :href='website'><i class='mdi mdi-web'/>Visit {{websiteHost}}</a>
          <a class='btn' :class='{primary:!website}' :href='githubUrl'><i class='mdi mdi-github'/>View on GitHub</a>
        </div>
      </div>
    </header>
    <div class='body'>
      <!-- Writeup, demo or the default short description -->
      <article class='writeup'>
        <component v-if='page' :is='page' :project='project'/>
        <template v-else>
          <p class='lede'>{{project.tagline}}</p>
          <p v-if='github?.description && github.description != project.tagline'>{{github.description}}</p>
        </template>
      </article>
      <!-- Side panel with GitHub details -->
      <aside class='side'>
        <div class='card'>
          <h4>From GitHub</h4>
          <dl class='facts'>
            <dt>Repository</dt><dd><a :href='githubUrl'>{{project.repo}}</a></dd>
            <template v-if='github?.license'><dt>License</dt><dd>{{github.license}}</dd></template>
            <template v-if='github?.pushed'><dt>Last push</dt><dd>{{utils.formatDate(github.pushed, 'YYYY-MM-DD')}}</dd></template>
            <template v-if='website'><dt>Website</dt><dd><a :href='website'>{{websiteHost}}</a></dd></template>
          </dl>
          <CommitChart :commits='commits'/>
        </div>
        <div class='card' v-if='project.install'>
          <h4>Install</h4>
          <div class='install'>
            <code>{{project.install}}</code>
            <button type='button' :aria-label='`Copy ${project.install}`' @click='copyInstall'>
              <i class='mdi' :class='copied ? "mdi-check" : "mdi-content-copy"'/>
            </button>
          </div>
        </div>
        <div class='card related' v-if='related.length'>
          <h4>More in {{github.language}}</h4>
          <router-link v-for='other in related' :key='other.slug' :to='`/projects/${other.slug}`'>
            {{other.name}}<span>&#9733; {{utils.intComma(other.github.stars)}}</span>
          </router-link>
        </div>
      </aside>
    </div>
  </div>
  <IconMessage v-else icon='mdi-folder-question-outline' text='Project not found' height='400px'/>
</template>

<script setup>
  import {computed, defineAsyncComponent, onBeforeMount, ref, watch} from 'vue'
  import {useRoute} from 'vue-router'
  import {IconMessage} from '@/components'
  import {useBackgrounds, useProjects} from '@/composables'
  import {api, utils} from '@/utils'
  import {CommitChart, LANGUAGE_COLORS, bannerStyle} from '@/views/projects'

  const RECENT_MS = 183 * 86400000          // Show the Updated pill for pushes within about six months
  const route = useRoute()
  const {projects} = useProjects()
  const {describe} = useBackgrounds()
  const commits = ref(null)                 // Commit counts per day for this project
  const copied = ref(false)                 // True briefly after copying the install command

  const project = computed(() => projects.value.find(p => p.slug == route.params.slug))
  const github = computed(() => project.value?.github)
  const githubUrl = computed(() => `https://github.com/${project.value.repo}`)
  const website = computed(() => project.value.website || github.value?.homepage)
  const websiteHost = computed(() => website.value ? new URL(website.value).hostname : null)
  const languageColor = computed(() => LANGUAGE_COLORS[github.value?.language] || 'var(--darkbg-fg4)')
  const recentlyUpdated = computed(() => github.value?.pushed && Date.now() - new Date(github.value.pushed) <= RECENT_MS)
  const page = computed(() => project.value?.page ? defineAsyncComponent(project.value.page) : null)

  onBeforeMount(function() { utils.setNavPosition('left') })

  // Related
  // Up to four other projects written in the same language
  const related = computed(function() {
    var language = github.value?.language
    if (!language) { return [] }
    return projects.value.filter(p => p.slug != project.value.slug && p.github?.language == language).slice(0, 4)
  })

  // Watch Project
  // Fetch the commit history whenever the project changes
  watch(() => project.value?.repo, async function(repo) {
    commits.value = null
    if (!repo) { return }
    try {
      var {data} = await api.Projects.getRepo(repo)
      if (repo == project.value?.repo) { commits.value = data.commits }
    } catch (err) {
      console.error(`Unable to load commits for ${repo}`, err)
    }
  }, {immediate:true})

  // Copy Install
  // Copy the install command and briefly show a checkmark
  function copyInstall() {
    utils.copyText(project.value.install)
    copied.value = true
    setTimeout(function() { copied.value = false }, 1500)
  }
</script>

<style>
  #project {
    background-color: var(--bgcolor);
    /* Banner header */
    .banner {
      align-items: flex-end;
      color: var(--darkbg-fg1);
      display: flex;
      height: 360px;
      overflow: hidden;
      position: relative;
      .bgimg, .shade { position:absolute; top:0px; left:0px; right:0px; bottom:0px; }
      .bgimg {
        background-color: #282828;
        background-position: center;
        background-size: cover;
        &.placeholder {
          background-color: #3c3836;
          background-image: repeating-linear-gradient(135deg, #fbf1c70d 0px 14px, transparent 14px 28px);
        }
      }
      .shade { background: linear-gradient(0deg, #1d2021eb 0%, #1d202173 55%, #1d202126 100%); }
      /* Where the banner photo was taken, styled like the footer map label on a dark
       * semi-transparent tag so it stays readable over bright photos */
      .credit {
        background-color: #0006;
        border-radius: 3px;
        color: var(--darkbg-fg2);
        font-family: var(--fontfamily-code);
        font-size: 9px;
        letter-spacing: 1px;
        padding: 4px 8px;
        position: absolute;
        right: 22px;
        text-transform: uppercase;
        top: 21px;
      }
      .inner {
        align-items: flex-end;
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        padding: 0px 64px 34px 64px;
        position: relative;
        width: 100%;
      }
      .title { flex: 1 1 420px; min-width:0px; }
      h1 {
        color: var(--darkbg-fg0);
        font-family: var(--fontfamily-title);
        font-size: 50px;
        font-weight: 700;
        line-height: 1.1;
        text-shadow: 0 2px 18px #0006;
      }
      .tagline {
        color: var(--darkbg-fg2);
        font-family: var(--fontfamily-article);
        font-size: 17px;
        margin-top: 10px;
        max-width: 640px;
      }
      .chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
      .chip {
        align-items: center;
        backdrop-filter: blur(6px);
        background-color: #1d202199;
        border: 1px solid #fbf1c724;
        border-radius: 999px;
        color: var(--darkbg-fg2);
        display: inline-flex;
        font-family: var(--fontfamily-article);
        font-size: 13px;
        gap: 6px;
        padding: 4px 13px;
        b { color:var(--darkbg-fg0); font-weight:600; }
        .mdi { font-size:15px; }
        .dot { border-radius:50%; height:8px; width:8px; }
      }
      .actions { display:flex; flex-direction:column; gap:10px; min-width:210px; }
      .btn, .btn:hover {
        align-items: center;
        background-color: #1d2021a6;
        border: 1px solid #fbf1c740;
        border-radius: 8px;
        color: var(--darkbg-fg0);
        display: inline-flex;
        font-family: var(--fontfamily-article);
        font-size: 14px;
        font-weight: 600;
        gap: 9px;
        justify-content: center;
        padding: 11px 18px;
        text-decoration: none;
        transition: transform .15s ease;
        .mdi { font-size:18px; }
        &.primary { background-color:#fe8019; border-color:#fe8019; color:#1d2021; }
      }
      .btn:hover { transform:translateY(-2px); }
    }

    /* Writeup and side panel */
    .body {
      align-items: start;
      display: grid;
      gap: 44px;
      grid-template-columns: minmax(0px, 1fr) 300px;
      max-width: 1260px;
      padding: 44px 64px 80px 64px;
    }
    article.writeup {
      color: var(--lightbg-fg1);
      font-size: 16px;
      padding: 0px;
      max-width: 720px;
      h2:first-child { margin-top:0px; }
      .lede {
        color: var(--lightbg-fg0);
        font-family: var(--fontfamily-title);
        font-size: 19px;
        font-weight: 300;
        line-height: 1.75;
        margin-top: 0px;
      }
      /* Placeholder prompts in writeups that have not been written yet */
      .draft {
        border: 1px dashed var(--lightbg-bg4);
        border-radius: 8px;
        color: var(--lightbg-fg4);
        font-style: italic;
        padding: 12px 16px;
        &::before { content:'Draft: '; font-style:normal; font-weight:600; }
      }
      pre {
        background-color: var(--darkbg-bgh);
        border-radius: 10px;
        color: var(--darkbg-fg1);
        font-family: var(--fontfamily-code);
        font-size: 13px;
        line-height: 1.7;
        margin: 10px 0px 20px 0px;
        overflow-x: auto;
        padding: 18px 20px;
        .comment { color:var(--darkbg-gray); }
      }
    }
    .side .card {
      background-color: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 10px #2828280f;
      font-family: var(--fontfamily-article);
      margin-bottom: 18px;
      padding: 20px 22px;
      h4 {
        color: var(--lightbg-fg4);
        font-family: var(--fontfamily-article);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        margin-bottom: 12px;
        text-transform: uppercase;
      }
      .facts {
        display: grid;
        font-size: 13.5px;
        gap: 6px 16px;
        grid-template-columns: auto 1fr;
        dt { color:var(--lightbg-fg4); text-transform:none; letter-spacing:normal; font-size:13.5px; }
        dd { color:var(--lightbg-fg1); margin:0px; overflow:hidden; text-align:right; text-overflow:ellipsis; white-space:nowrap; }
      }
      .install {
        align-items: center;
        background-color: var(--lightbg-bg0);
        border: 1px solid #ebebe4;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        padding: 4px 4px 4px 12px;
        code { font-family:var(--fontfamily-code); font-size:12.5px; overflow-x:auto; white-space:nowrap; }
        button {
          background: none;
          border: 0px;
          color: var(--lightbg-fg3);
          cursor: pointer;
          font-size: 16px;
          padding: 4px 8px;
        }
      }
      &.related a, &.related a:hover {
        text-decoration: none;
        border-bottom: 1px solid var(--lightbg-bg1);
        color: var(--lightbg-fg1);
        display: flex;
        font-size: 14px;
        justify-content: space-between;
        padding: 7px 0px;
        &:last-child { border-bottom:0px; }
        span { color:var(--lightbg-fg4); font-family:var(--fontfamily-code); font-size:12px; }
      }
    }
  }

  @media (max-width: 1100px) {
    #project .body { grid-template-columns:1fr; padding:30px 20px 60px 20px; }
    #project .banner .inner { padding:0px 20px 30px 20px; }
    #project .banner h1 { font-size:38px; }
  }
</style>
