<template>
  <div id='footer' class='darkbg'>
    <div class='footer-section' style='width:400px'>
      <div class='site'>
        <h4>PushingKarma</h4>
        Site created using <a href='https://www.djangoproject.com/'>Django</a>, <a href='https://graphql.org/'>Graphql</a>,
        <a href='https://vuejs.org/'>Vue</a>, and is hosted on <a href='https://www.digitalocean.com/'>Digital Ocean</a>.
        Original <a href='https://themeforest.net/item/arlo-personal-portfolio-template/23175475'>Arlo design</a> heavily
        modified by me.<br/>
        <div style='margin-top:5px;'>
          <i class='mdi mdi-email'></i> {{email}}<span style='display:none;'>+site</span>@gmail.com
        </div>
      </div>
    </div>
    <div class='footer-section' style='width:250px'>
      <div class='social'>
        <h4>Social Media</h4>
        <li><a href='https://github.com/pkkid'><i class='mdi mdi-github-box'></i> Github</a></li>
        <li><a href='https://www.linkedin.com/in/shepanski'><i class='mdi mdi-linkedin-box'></i> Linked In</a></li>
        <li><a href='https://www.facebook.com/mshepanski'><i class='mdi mdi-facebook-box'></i> Facebook</a></li>
      </div>
    </div>
    <div class='footer-section' style='width:350px'>
      <div class='attribution'>
        <h4>Legal</h4>
        Copyright (c) 2019 PushingKarma. All rights reserved.
        <a href='#'>Privacy Policy & Terms of Service</a>.
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
    font-size: 0.9em;
    line-height: 1.5;
    width: 1000px;
    margin: 0px auto;

    .footer-section {
      float:left;
      height: 250px;
      padding: 50px 0px 100px 0px;
      position: relative;
      & > div { padding:0px 50px; border-right:1px solid lighten($darkbg-color, 7%); }
      &:last-child > div { border-right: 0px; }

      h4 {
        position: relative;
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
      font-size: 1em;
    }
  }
</style>
