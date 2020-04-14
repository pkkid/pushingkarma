<template>
  <div id='footer' class='darkbg'>
    <div class='footer-section' style='width:400px'>
      <div class='site'>
        <h4>PushingKarma</h4>
        Site created using <a href='https://www.djangoproject.com/'>Django</a>,
        <a href='https://www.django-rest-framework.org/'>Django Rest Framework</a>,
        <a href='https://vuejs.org/'>Vue</a>, <a href='https://buefy.org/'>Beufy</a>,
        and is hosted on <a href='https://www.digitalocean.com/'>Digital Ocean</a>.
        <div style='margin-top:5px;'>
          <i class='mdi mdi-email'></i> {{email}}<span style='display:none;'>+site</span>@gmail.com
        </div>
      </div>
    </div>
    <div class='footer-section' style='width:250px'>
      <div class='social'>
        <h4>Social Media</h4>
        <li><i class='mdi mdi-github-box'/> <a href='https://github.com/pkkid'>Github</a></li>
        <li><i class='mdi mdi-linkedin-box'/> <a href='https://www.linkedin.com/in/shepanski'>Linked In</a></li>
        <li><i class='mdi mdi-facebook-box'/> <a href='https://www.facebook.com/mshepanski'>Facebook</a></li>
      </div>
    </div>
    <div class='footer-section' style='width:350px'>
      <div class='attribution'>
        <h4>Legal</h4>
        Copyright (c) 2020 PushingKarma. All rights reserved.
        <router-link to='/privacy'>Terms of Service & Privacy Policy</router-link>.
      </div>
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
    text-align: left;
    font-size: 0.9rem;
    font-family: Roboto;
    color: $darkbg-text;
    line-height: 1.5;
    width: 1000px;
    margin: 0px auto;

    .footer-section {
      float:left;
      height: 250px;
      margin-bottom: 40px;
      padding: 50px 0px 100px 0px;
      position: relative;
      & > div { padding:0px 50px; border-right:1px solid lighten($darkbg-color, 7%); }
      &:last-child > div { border-right: 0px; }

      h4 {
        position: relative;
        margin-bottom: 15px;
        font-family: Roboto;
        font-size: 15px;
        font-weight: 400;
        color: #ebdbb2;
        &::before {
          content: ' ';
          display: block;
          position: absolute;
          width: 30px;
          height: 1px; 
          background-color: $darkbg-accent;
          bottom: -3px;
        }
      }
    }
    li {
      list-style-type: none;
    }
    .mdi {
      font-size: 1.4em;
      margin-right: 5px;
      position: relative;
      top: 2px;
    }
  }
</style>
