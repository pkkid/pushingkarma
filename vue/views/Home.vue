<template>
  <div id='home' class='lightbg'>
    <!-- Splash -->
    <div id='splash'>
      <div class='bgimg'/>
      <div class='mist'/>
      <div class='shade'/>
      <div class='dust'>
        <span v-for='(mote, i) in motes' :key='i' class='mote' :style='mote.wrap'>
          <span :class='mote.cls' :style='mote.dot'/>
        </span>
      </div>
      <div class='content'>
        <div class='intro'>
          <div class='kicker'>Boston based developer &amp; builder</div>
          <div class='name'>Michael <span>Shepanski</span></div>
          <p>I love building things that make my own life a little easier, and I love sharing
            them even more, in case they make yours easier too. Some of them even work on the
            first try.</p>
        </div>
        <img class='photo' src='/static/img/photo.jpg'>
      </div>
    </div>
    <!-- Recent Projects -->
    <article id='projects'>
      <h1>Recent Projects <div class='subtext'>What I have been building lately</div></h1>
      <div class='recentlist'>
        <router-link v-for='project in recent' :key='project.slug' :to='`/projects/${project.slug}`' class='recent'>
          <div class='banner'>
            <div class='bgimg' :class='{placeholder:!project.banner}' :style='bannerStyle(project)'/>
            <div class='title'>{{project.name}}</div>
          </div>
          <div class='details'>
            <p>{{project.tagline}}</p>
            <div class='meta' v-if='project.github'>
              <span v-if='project.github.language'><span class='dot' :style='{backgroundColor:LANGUAGE_COLORS[project.github.language]}'/>{{project.github.language}}</span>
              <span v-if='project.github.stars'>&#9733; {{utils.intComma(project.github.stars)}}</span>
            </div>
          </div>
        </router-link>
      </div>
      <!-- Smaller Projects -->
      <h1>Smaller Projects <div class='subtext'>Little tools I keep coming back to</div></h1>
      <div class='smalllist'>
        <router-link v-for='project in small' :key='project.slug' :to='`/projects/${project.slug}`' class='small'>
          <ProjectIcon :project='project'/>
          <div class='title'>{{project.name}}</div>
          <p>{{project.tagline}}</p>
          <div class='meta' v-if='project.github'>
            <span v-if='project.github.language'>{{project.github.language}}</span>
            <span v-if='project.github.stars'>&#9733; {{project.github.stars}}</span>
            <span v-if='project.github.pushed'>updated {{utils.timeAgo(new Date(project.github.pushed).getTime(), true)}}</span>
          </div>
        </router-link>
      </div>
    </article>
    <!-- About Me -->
    <article id='about'>
      <h1>About Me <div class='subtext'>My background and motivation</div></h1>
      <div class='photowrap'>
        <div class='photo gridbg'>
          <img src='/static/img/family.jpg'/>
        </div>
        <div class='aboutme'>
          <h2>I am Michael Shepanski, <span class='accent'>Developer</span></h2>
          <p style='max-width:600px; min-width:450px;'>
            I've been writing software around Boston and the Northeast since 2002, and I
            still feel like I'm learning something new every week. I enjoy building tools
            that make life a little easier, stretching them to do more than I first intended,
            and making them look good while I'm at it.
          </p>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup>
  import {computed, onBeforeMount} from 'vue'
  import {useProjects} from '@/composables'
  import {utils} from '@/utils'
  import {LANGUAGE_COLORS, ProjectIcon, bannerStyle} from '@/views/projects'

  const motes = createMotes(15)                             // Dust particles floating over the splash image
  const {projects} = useProjects()                          // Projects with their GitHub stats
  const recent = computed(() => sortByPushed(projects.value.filter(p => p.section == 'recent')))
  const small = computed(() => projects.value.filter(p => p.section == 'small'))

  onBeforeMount(function() { utils.setNavPosition('left') })

  // Sort By Pushed
  // Most recently pushed projects first; projects without stats keep their order
  function sortByPushed(list) {
    return [...list].sort(function(a, b) {
      return new Date(b.github?.pushed || 0) - new Date(a.github?.pushed || 0)
    })
  }

  // Create Motes
  // Build dust particles from a seeded random so they land in the same places on
  // every load. Negative delays start each one partway through its float.
  function createMotes(count) {
    var seed = 7
    var rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647
    return Array.from({length:count}, function() {
      var duration = 16 + rand() * 18
      var size = (1.2 + rand() * 2.4).toFixed(1)
      var glow = rand() < 0.3 ? 'glow' : ''
      return {
        cls: ['dot', ['float1', 'float2', 'float3', 'float4'][Math.floor(rand() * 4)], glow],
        wrap: {left:`${rand() * 100}%`, top:`${20 + rand() * 85}%`, opacity:(0.35 + rand() * 0.45).toFixed(2)},
        dot: {width:`${size}px`, height:`${size}px`, animationDuration:`${duration}s`, animationDelay:`${-rand() * duration}s`},
      }
    })
  }
</script>

<style>
  #home {
    #splash {
      height: 470px;
      overflow: hidden;
      position: relative;

      .bgimg, .mist, .shade, .dust {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
      }
      .bgimg {
        background-color: #282828;
        background-image: url('/static/img/backgrounds/china-2007-landscape.png');
        background-position: center 40%;
        background-size: cover;
      }
      .mist {
        animation: splash-mist 28s ease-in-out infinite alternate;
        background:
          radial-gradient(ellipse 40% 18% at 30% 70%, #ebdbb238, transparent 70%),
          radial-gradient(ellipse 35% 14% at 75% 60%, #ebdbb229, transparent 70%);
        left: -40%; right: -40%;
      }
      /* Dark fade in from the left (behind the text) plus the fade to dark at the bottom */
      .shade {
        background:
          linear-gradient(90deg, #1d2021b3 0%, #1d202159 35%, #1d202100 75%),
          linear-gradient(180deg, #1d202126 0%, #1d202159 55%, #1d2021 100%);
      }
      .dust {
        overflow: hidden;
        pointer-events: none;
        .mote { position: absolute; }
        .dot {
          animation-iteration-count: infinite;
          animation-timing-function: ease-in-out;
          background-color: #fff;
          border-radius: 50%;
          display: block;
          opacity: 0;
        }
        .glow { box-shadow: 0 0 6px 1px #ffffffa6; }
        .float1 { animation-name: splash-float1; }
        .float2 { animation-name: splash-float2; }
        .float3 { animation-name: splash-float3; }
        .float4 { animation-name: splash-float4; }
      }
      .content {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        gap: 40px;
        height: 100%;
        justify-content: space-between;
        margin: 0px auto;
        max-width: 1030px;
        padding: 0px 40px 70px 40px;
        position: relative;
      }
      .intro {
        max-width: 640px;
        text-shadow: 0 0 40px #0009;
        .kicker {
          color: #fe8019;
          font-family: var(--fontfamily-code);
          font-size: 12px;
          letter-spacing: 2px;
          margin-bottom: 14px;
          text-transform: uppercase;
        }
        .name {
          color: #fbf1c7;
          font-family: var(--fontfamily-title);
          font-size: 38px;
          font-weight: 300;
          line-height: 1.05;
          span { color: #fe8019; font-weight: 400; }
        }
        p {
          color: #ebdbb2;
          font-family: var(--fontfamily-article);
          font-size: 16px;
          line-height: 1.6;
          margin: 16px 0px 24px 0px;
          max-width: 500px;
        }
      }
      .photo {
        border-radius: 100%;
        border: 6px solid #665c54d9;
        box-shadow: 0 20px 50px #0006;
        flex-shrink: 0;
        width: 130px;
      }
    }

    /* Projects and About share the splash content's centered column */
    #projects, #about {
      margin: 0px auto;
      max-width: 1030px;
    }

    h1 { font-size: 32px }
    h1 .subtext { font-size: 13px; }
    h2 { font-size: 21px; }
    p { font-size: 15px; }

    #about {
      padding-bottom: 90px;
      /* Text drops below the photo when there isn't room beside it */
      .photowrap {
        display: flex;
        flex-wrap: wrap;
        margin-top: 30px;
        row-gap: 40px;
        .photo {
          border: 10px solid #282828;
          box-sizing: border-box;
          flex-shrink: 0;
          height: 210px;
          margin-top: 30px;
          margin-right: 50px;
          position: relative;
          top:-10px; left:10px;
          width: 280px;
          img {
            position: relative;
            width: 280px;
            top:-20px; left:-20px;
          }
        }
        .aboutme {
          flex: 1 1 400px;
          min-width: 0px;
          h2 {
            line-height: 1.2;
            margin-top: 6px;
            .accent { color: #d65d0e; }
          }
        }
      }
    }

    #projects {
      h1 + .recentlist, h1 + .smalllist { margin-top: 30px; }
      .smalllist + * , .recentlist + h1 { margin-top: 60px; }
      a, a:hover { color: inherit; text-decoration: none; }
      .meta {
        align-items: center;
        color: var(--lightbg-fg4);
        display: flex;
        flex-wrap: wrap;
        font-size: 12px;
        gap: 2px 14px;
        span { align-items:center; display:inline-flex; gap:6px; white-space:nowrap; }
        .dot { border-radius:50%; height:8px; width:8px; }
      }
      /* Recent projects: banner cards, four across on wide screens */
      .recentlist {
        display: grid;
        gap: 20px;
        grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      }
      .recent {
        background-color: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 10px #28282812;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transition: transform .25s ease, box-shadow .25s ease;
        &:hover { box-shadow:0 20px 40px #28282824; transform:translateY(-5px); }
        .banner {
          align-items: flex-end;
          display: flex;
          height: 120px;
          padding: 12px 16px;
          position: relative;
        }
        .bgimg {
          background-color: #282828;
          background-position: center;
          background-size: cover;
          position: absolute;
          top:0px; left:0px; right:0px; bottom:0px;
          &::after {
            background: linear-gradient(0deg, #1d2021eb 0%, #1d202173 55%, #1d202126 100%);
            content: '';
            position: absolute;
            top:0px; left:0px; right:0px; bottom:0px;
          }
          &.placeholder {
            background-color: #3c3836;
            background-image: repeating-linear-gradient(135deg, #fbf1c70d 0px 14px, transparent 14px 28px);
          }
        }
        .title {
          color: var(--darkbg-fg0);
          font-family: var(--fontfamily-title);
          font-size: 20px;
          font-weight: 700;
          position: relative;
          text-shadow: 0 2px 10px #0008;
        }
        .details { display:flex; flex:1; flex-direction:column; gap:10px; padding:14px 16px 16px 16px; }
        p { color:var(--lightbg-fg2); flex:1; font-size:13.5px; line-height:1.6; margin:0px; }
      }
      /* Smaller projects: compact cards with a colored icon */
      .smalllist {
        display: grid;
        gap: 14px;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      }
      .small {
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 1px 4px #2828280f;
        column-gap: 14px;
        display: grid;
        grid-template-columns: 34px 1fr;
        grid-template-rows: auto 1fr auto;
        padding: 16px 18px;
        transition: transform .2s ease, box-shadow .2s ease;
        &:hover { box-shadow:0 12px 24px #2828281a; transform:translateY(-3px); }
        .projecticon { font-size:30px; grid-row:span 3; justify-self:center; line-height:1; margin-top:-2px; }
        .title { color:var(--lightbg-fg0); font-family:var(--fontfamily-title); font-size:16px; }
        p { color:var(--lightbg-fg3); font-size:13px; line-height:1.5; margin:4px 0px 0px 0px; }
        .meta { font-family:var(--fontfamily-code); font-size:11.5px; margin-top:8px; }
      }
    }
  }

  /* Splash Animations */
  @keyframes splash-mist {
    from { transform: translateX(-6%); }
    to { transform: translateX(6%); }
  }
  @keyframes splash-float1 {
    0% { transform: translate(0px, 0px); opacity: 0; }
    15% { opacity: 1; }
    50% { transform: translate(18px, -70px); }
    85% { opacity: 1; }
    100% { transform: translate(-6px, -150px); opacity: 0; }
  }
  @keyframes splash-float2 {
    0% { transform: translate(0px, 0px); opacity: 0; }
    20% { opacity: 1; }
    50% { transform: translate(-22px, -55px); }
    80% { opacity: 1; }
    100% { transform: translate(10px, -120px); opacity: 0; }
  }
  @keyframes splash-float3 {
    0% { transform: translate(0px, 0px); opacity: 0; }
    15% { opacity: 1; }
    40% { transform: translate(12px, -40px); }
    70% { transform: translate(-14px, -90px); }
    85% { opacity: 1; }
    100% { transform: translate(4px, -170px); opacity: 0; }
  }
  @keyframes splash-float4 {
    0% { transform: translate(0px, 0px); opacity: 0; }
    25% { opacity: 1; }
    50% { transform: translate(28px, -45px); }
    75% { opacity: 1; }
    100% { transform: translate(40px, -95px); opacity: 0; }
  }
  @media (prefers-reduced-motion: reduce) {
    #home #splash .mist { animation: none; }
    #home #splash .dust .dot { animation: none; opacity: 0.6; }
  }
</style>
