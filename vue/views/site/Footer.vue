<template>
  <div id='footer' class='darkbg'>
    <!-- Boston Harbor coastline, fading out toward the ocean -->
    <div class='harbormap'><img src='/static/img/boston-harbor.svg'/></div>
    <div class='maplabel'>
      Boston Harbor · 42.33° N 71.02° W<br/>
      <span>Map data © OpenStreetMap contributors</span>
    </div>
    <div class='footerwrap'>
      <div class='footercolumn' style='width:400px'>
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
      <div class='footercolumn' style='width:250px'>
        <h4>Social Media</h4>
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
      <div class='footercolumn' style='width:350px'>
        <h4>Legal</h4>
        Copyright (c) 2020-{{year}} PushingKarma. All rights reserved.
      </div>
      <div style='clear:left;'/>
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
    overflow: hidden;
    padding-left: 300px;
    position: relative;
    text-align: left;

    .harbormap {
      mask-image: linear-gradient(90deg, #000 0%, #000 28%, transparent 88%);
      opacity: 0.1;
      overflow: hidden;
      pointer-events: none;
      position: absolute;
      top: 0px; left: 300px; right: 0px; bottom: 0px;
      img {
        max-width: none;
        position: absolute;
        top: -290px; left: -40px;
        width: 1200px;
      }
    }
    .maplabel {
      bottom: 14px;
      color: var(--darkbg-fg4);
      font-family: var(--fontfamily-code);
      font-size: 10px;
      letter-spacing: 1.5px;
      line-height: 1.6;
      position: absolute;
      right: 24px;
      text-align: right;
      text-transform: uppercase;
      span { letter-spacing: 0.5px; text-transform: none; }
    }
    .footerwrap {
      margin: 0px auto;
      position: relative;
      width: 1005px;
    }
    .footercolumn {
      float:left;
      padding: 50px;
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

  @media print {
    #footer { display: none; }
  }
</style>
