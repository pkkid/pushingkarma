<template>
  <div id='footer' class='darkbg'>
    <div class='footerwrap'>
      <div class='footercolumn' style='width:400px'>
        <h4>PushingKarma</h4>
        Site created using <a href='https://www.djangoproject.com/'>Django</a>,
        <a href='https://www.django-rest-framework.org/'>Django Rest Framework</a>,
        <a href='https://vuejs.org/'>Vue</a> and hosted on
        <a href='https://www.digitalocean.com/'>Digital Ocean</a>.
        <div style='margin-top:5px;'>
          <i class='mdi mdi-email-outline'/>
          {{email}}<span style='display:none;'>+site</span>@gmail.com
        </div>
      </div>
      <div class='footercolumn' style='width:250px'>
        <h4>Social Media</h4>
        <div>
          <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>
            <path d='M12,2A10,10 0 0,0 2,12C2,16.42 4.87,20.17 8.84,21.5C9.34,21.58 9.5,21.27 9.5,21C9.5,20.77 9.5,
              20.14 9.5,19.31C6.73,19.91 6.14,17.97 6.14,17.97C5.68,16.81 5.03,16.5 5.03,16.5C4.12,15.88 5.1,15.9 5.1,
              15.9C6.1,15.97 6.63,16.93 6.63,16.93C7.5,18.45 8.97,18 9.54,17.76C9.63,17.11 9.89,16.67 10.17,16.42C7.95,
              16.17 5.62,15.31 5.62,11.5C5.62,10.39 6,9.5 6.65,8.79C6.55,8.54 6.2,7.5 6.75,6.15C6.75,6.15 7.59,
              5.88 9.5,7.17C10.29,6.95 11.15,6.84 12,6.84C12.85,6.84 13.71,6.95 14.5,7.17C16.41,5.88 17.25,6.15 17.25,
              6.15C17.8,7.5 17.45,8.54 17.35,8.79C18,9.5 18.38,10.39 18.38,11.5C18.38,15.32 16.04,16.16 13.81,
              16.41C14.17,16.72 14.5,17.33 14.5,18.26C14.5,19.6 14.5,20.68 14.5,21C14.5,21.27 14.66,21.59 15.17,
              21.5C19.14,20.16 22,16.42 22,12A10,10 0 0,0 12,2Z' />
          </svg>
          <a href='https://github.com/pkkid'>Github</a>
        </div>
        <div>
          <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>
            <path d='M19 3A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3H19M18.5 18.5V13.2A3.26
              3.26 0 0 0 15.24 9.94C14.39 9.94 13.4 10.46 12.92 11.24V10.13H10.13V18.5H12.92V13.57C12.92 12.8 13.54
              12.17 14.31 12.17A1.4 1.4 0 0 1 15.71 13.57V18.5H18.5M6.88 8.56A1.68 1.68 0 0 0 8.56 6.88C8.56 5.95 7.81
              5.19 6.88 5.19A1.69 1.69 0 0 0 5.19 6.88C5.19 7.81 5.95 8.56 6.88 8.56M8.27 18.5V10.13H5.5V18.5H8.27Z' />
            </svg>
          <a href='https://www.linkedin.com/in/shepanski'>Linked In</a>
        </div>
        <div>
          <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>
            <path d='M12 2.04C6.5 2.04 2 6.53 2 12.06C2 17.06 5.66 21.21 10.44 21.96V14.96H7.9V12.06H10.44V9.85C10.44
            7.34 11.93 5.96 14.22 5.96C15.31 5.96 16.45 6.15 16.45 6.15V8.62H15.19C13.95 8.62 13.56 9.39 13.56
            10.18V12.06H16.34L15.89 14.96H13.56V21.96A10 10 0 0 0 22 12.06C22 6.53 17.5 2.04 12 2.04Z' />
          </svg>
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
    text-align: left;
    padding-left: 300px;

    .footerwrap {
      margin: 0px auto;
      width: 1005px;
    }
    .footercolumn {
      float:left;
      padding: 50px;
      position: relative;
      svg {
        fill: var(--fgcolor);
        margin-right: 8px;
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
