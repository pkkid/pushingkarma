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
          <router-link to='/#projects' class='cta'>See my projects</router-link>
        </div>
        <img class='photo' src='/static/img/photo.jpg'>
      </div>
    </div>
    <!-- Projects -->
    <article id='projects'>
      <h1>Projects <div class='subtext'>Whats been keeping me busy</div></h1>
      <div class='projectlist'>
        <div><a href='https://github.com/pkkid/dalica'>
          <i class='mdi mdi-image-multiple-outline'/>
          <div class='title'>Dalica</div>
          <p>A fast, local-first photo organizer written in Rust. Star, tag and caption the photos in your own folders.</p>
        </a></div>
        <div><a href='https://vowelit.pkarma.com'>
          <i class='mdi mdi-alphabetical-variant'/>
          <div class='title'>Vowelit</div>
          <p>A word game for Android, iOS and the web. Find words on a letter grid solo, or challenge your friends.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/claude-aitools'>
          <i class='mdi mdi-toolbox-outline'/>
          <div class='title'>Claude AITools Mod</div>
          <p>A Claude Code mod that adds a slim bar showing usage and cost, plus task checklists and branch cleanup.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/python-plexapi'>
          <i class='mdi mdi-code-block-braces'/>
          <div class='title'>Python PlexAPI</div>
          <p>Python bindings for the Plex Server API. Navigate and manage your local or remote shared libraries.</p>
        </a></div>
        <div><a href='https://github.com/django-dbbackup/django-dbbackup'>
          <i class='mdi mdi-database-outline'/>
          <div class='title'>Django DBBackup</div>
          <p>Management commands to backup and restore project database to AmazonS3, Dropbox or Local Disk.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/pygrid'>
          <i class='mdi mdi-view-dashboard-outline'/>
          <div class='title'>PyGrid</div>
          <p>Easily organize open windows by tiling and positioning them to make the best use of your desktop.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/link-manager'>
          <i class='mdi mdi-vector-link'/>
          <div class='title'>Link Manager</div>
          <p>Collection of scripts to help easily sync specific configuration files across all your Linux computers.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/django-searchquery'>
          <i class='mdi mdi-magnify'/>
          <div class='title'>Django Searchquery</div>
          <p>Provides advanced search and filtering capabilities to structured data in Django models.</p>
        </a></div>
        <div><a href='https://github.com/pkkid/pkmeter-conky'>
          <i class='mdi mdi-speedometer-slow'/>
          <div class='title'>PKMeter-Conky</div>
          <p>Collection of scripts and a Conky configuration. Makes fetching data easy and results stored as json.</p>
        </a></div>
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
  import {inject, onBeforeMount} from 'vue'
  import {utils} from '@/utils'

  const motes = createMotes(15)                             // Dust particles floating over the splash image

  onBeforeMount(function() { utils.setNavPosition('left') })

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
        background-image: url('/static/img/mtn-landscape.png');
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
      .shade {
        background: linear-gradient(180deg, #1d202126 0%, #1d202159 55%, #1d2021 100%);
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
        .cta, .cta:hover {
          background-color: #fe8019;
          border-bottom: none;
          border-radius: 8px;
          color: #1d2021;
          display: inline-block;
          font-family: var(--fontfamily-article);
          font-size: 14px;
          font-weight: 600;
          padding: 11px 20px;
          text-shadow: none;
        }
        .cta:hover {
          box-shadow: 0 8px 20px #0004;
          transform: translateY(-2px);
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
          height: 240px;
          margin-top: 30px;
          margin-right: 60px;
          position: relative;
          top:-10px; left:20px;
          width: 320px;
          img {
            position: relative;
            width: 320px;
            top:-24px; left:-24px;
          }
        }
      }
    }

    #projects {
      /* As many 300px+ columns as fit, at most three, stacking on narrow screens */
      .projectlist {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        grid-gap: 20px;
        margin-top: 30px;
        max-width: 950px;
      }
      a {
        background-color: #fff;
        box-shadow: 0 0 20px #ccc;
        box-sizing: border-box;
        color: #504945;
        display: block;
        padding: 22px 26px 22px 26px;
        position: relative;
        text-decoration: none !important;
        top: 0px;
        transition: all .2s ease;

        .mdi{
          font-size: 2.2rem;
          position: relative;
          left: -4px;
        }
        .title {
          color: #363636;
          font-size: 1.15rem;
          font-weight: 400;
          left: -1px;
          line-height: 1;
          margin: 8px 0px 10px 0px;
          position: relative;
        }
        p {
          font-size: 13px;
          font-weight: 400;
          min-height: 66px;
          letter-spacing: 0.3px;
          line-height: 1.7;
          word-wrap: break-word;
        }
        &:hover {
          top: -6px;
        }
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
