<template>
  <div id='footer' class='darkbg'>
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
    padding-left: 300px;
    position: relative;
    text-align: left;

    .footerwrap {
      margin: 0px auto;
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
</style>
