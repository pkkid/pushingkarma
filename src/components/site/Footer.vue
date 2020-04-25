<template>
  <div id='footer'>
    <div class='footerwrap'>
      <div class='footercolumn' style='width:400px'>
        <h4>PushingKarma</h4>
        Site created using <a href='https://www.djangoproject.com/'>Django</a>,
        <a href='https://www.django-rest-framework.org/'>Django Rest Framework</a>,
        <a href='https://vuejs.org/'>Vue</a>, <a href='https://buefy.org/'>Beufy</a>,
        and is hosted on <a href='https://www.digitalocean.com/'>Digital Ocean</a>.
        <div style='margin-top:5px;'>
          <i class='mdi mdi-email'></i> {{email}}<span style='display:none;'>+site</span>@gmail.com
        </div>
      </div>
      <div class='footercolumn' style='width:250px'>
        <h4>Social Media</h4>
        <div><i class='mdi mdi-github-box'/> <a href='https://github.com/pkkid'>Github</a></div>
        <div><i class='mdi mdi-linkedin-box'/> <a href='https://www.linkedin.com/in/shepanski'>Linked In</a></div>
        <div><i class='mdi mdi-facebook-box'/> <a href='https://www.facebook.com/mshepanski'>Facebook</a></div>
      </div>
      <div class='footercolumn' style='width:350px'>
        <h4>Legal</h4>
        Copyright (c) 2020 PushingKarma. All rights reserved.
      </div>
      <div style='clear:left;'/>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'Footer',
    data: () => ({
      email: atob('bWljaGFlbC5zaGVwYW5za2k='),
    }),
  };
</script>

<style lang='scss'>
  #footer {
    background-color: $darkbg-bg0;
    color: $darkbg-fg0;
    font-family: $fontfamily-article;
    font-size: 0.8rem;
    line-height: 1.5;
    text-align: left;

    a,a:visited {
      color: $darkbg-fg0;
      text-decoration: none;
      transition: color 0.2s ease;
      &:hover { color: $darkbg-orange1; }
    }
    .footerwrap {
      margin: 0px auto;
      width: 1005px;
    }
    .footercolumn {
      float:left;
      padding: 50px;
      position: relative;
    }
    h4 {
      color: $darkbg-fg0;
      font-family: $fontfamily-artsy;
      font-size: 1rem;
      font-weight: 400;
      margin-bottom: 15px;
      position: relative;
      &::before {
        background-color: $darkbg-accent;
        bottom: -3px;
        content: ' ';
        display: block;
        height: 1px; 
        position: absolute;
        width: 30px;
      }
    }
    .mdi {
      font-size: 1.4em;
      margin-right: 5px;
      position: relative;
      top: 2px;
    }
  }
</style>
