<template>
  <div id='footer' class='darkbg'>
    <!-- Boston Harbor coastline, fading out toward the ocean -->
    <div class='harbormap'><img src='/static/img/boston-harbor.svg'/></div>
    <div class='maplabel'>
      Boston Harbor · 42.33° N 71.02° W<br/>
      <span>Map data © OpenStreetMap contributors</span>
    </div>
    <div class='footerwrap'>
      <div class='footercolumn'>
        <h4>PushingKarma</h4>
        Created with <i class='mdi mdi-heart'/> using<br/>
        <a href='https://www.djangoproject.com/'>Django</a>,
        <a href='https://django-ninja.dev'>Django Ninja</a>, and
        <a href='https://vuejs.org/'>Vue</a>.
        <div style='margin-top:5px;'>
          <i class='mdi mdi-email-outline'/>
          {{email}}<span style='display:none;'>+site</span>@gmail.com
        </div>
      </div>
      <div class='footercolumn'>
        <h4>Social Media</h4>
        <div>
          <i class='mdi mdi-file-account-outline linkicon'/>
          <router-link to='/resume'>Resume</router-link>
        </div>
        <div>
          <i class='icon' style='--img:url(/static/img/icons/github.svg)' />
          <a href='https://github.com/pkkid'>Github</a>
        </div>
        <div>
          <i class='icon' style='--img:url(/static/img/icons/linkedin.svg)' />
          <a href='https://www.linkedin.com/in/shepanski'>Linked In</a>
        </div>
        <div>
          <i class='icon' style='--img:url(/static/img/icons/facebook.svg)' />
          <a href='https://www.facebook.com/mshepanski'>Facebook</a>
        </div>
      </div>
      <div class='footercolumn'>
        <h4>Legal</h4>
        Copyright (c) 2020-{{year}} PushingKarma. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup>
  import {ref} from 'vue'
  const email = ref(atob('bWljaGFlbC5zaGVwYW5za2k='))
  const year = new Date().getFullYear()
</script>
  
<style>
  #footer {
    font-family: var(--fontfamily-article);
    font-size: 0.85rem;
    font-weight: 400;
    line-height: 1.7;
    padding-left: 300px;
    position: relative;
    text-align: left;

    /* One map that scrolls with the footer. It rises 450px above the footer only
     * over the left nav column (clip-path), fades toward the ocean on the right and
     * toward the top over the nav, and sits above the fixed nav so it shows there. */
    .harbormap {
      clip-path: polygon(0px 0px, 300px 0px, 300px 450px, 100% 450px, 100% 100%, 0px 100%);
      mask-image:
        linear-gradient(90deg, #000 0%, #000 43%, transparent 90%),
        linear-gradient(0deg, #000 0px, #000 270px, transparent 100%);
      mask-composite: intersect;
      opacity: 0.06;
      overflow: hidden;
      pointer-events: none;
      position: absolute;
      top: -450px; left: 0px; right: 0px; bottom: 0px;
      z-index: 11;
      img {
        max-width: none;
        position: absolute;
        bottom: -464px; left: 0px;
        width: 1200px;
      }
    }
    .maplabel {
      bottom: 14px;
      color: var(--darkbg-fg4);
      font-family: var(--fontfamily-code);
      font-size: 7px;
      letter-spacing: 1px;
      line-height: 1.5;
      position: absolute;
      right: 24px;
      text-align: right;
      text-transform: uppercase;
      span { letter-spacing: 0.5px; text-transform: none; }
    }
    /* Same centered column as the homepage content, so the first column lines up
     * with the sections above. Three columns side by side, stacking into one when
     * the window gets narrow (see the media query below). */
    .footerwrap {
      column-gap: 40px;
      display: grid;
      grid-template-columns: 4fr 2.5fr 3.5fr;
      margin: 0px auto;
      max-width: 1030px;
      padding: 50px 40px 100px 40px;
      position: relative;
      row-gap: 30px;
      z-index: 12;
    }
    .footercolumn {
      min-width: 0px;
      position: relative;
      .icon {
        background-color: var(--fgcolor);
        display: inline-block;
        height: 16px;
        margin-right: 8px;
        mask: var(--img) no-repeat center / contain;
        position: relative;
        top: 3px;
        width: 16px;
      }
      .linkicon {
        display: inline-block;
        font-size: 18px;
        line-height: 16px;
        margin-left: -1px;
        margin-right: 7px;
        width: 16px;
      }
    }
    h4 {
      font-family: var(--fontfamily-artsy);
      font-size: 1rem;
      font-weight: 400;
      margin-bottom: 15px;
      position: relative;
      &::before {
        background-color: var(--accent);
        bottom: -3px;
        content: ' ';
        display: block;
        height: 1px;
        position: absolute;
        width: 30px;
      }
    }
  }

  /* Top navigation has no left column for the map to rise into */
  body.topnav #footer .harbormap {
    clip-path: none;
    top: 0px;
  }

  @media (max-width: 1000px) {
    #footer .footerwrap { grid-template-columns: 1fr; }
  }

  @media print {
    #footer { display: none; }
  }
</style>
