<template>
  <!-- Splash -->
  <div id='splash'>
    <div class='bgimg'/>
    <div class='content'>
      <img class='photo' src='/static/img/photo.jpg'>
      <div class='name'>Michael <span>Shepanski</span></div>
    </div>
  </div>
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
          I've been developing software in the Boston area for over 14 years,
          using Python since 2004 & Django since early 2009. Web development
          used to be a hobby to me. As web applications started becoming more
          complex and the demand so high, it turned into a full-time job. My
          passion is finding simple and elegant ways to display complex information.
        </p>
      </div>
    </div>
  </article>
  <!-- Projects -->
  <article id='projects'>
    <h1>Projects <div class='subtext'>Whats been keeping me busy</div></h1>
    <div class='projectlist' style='min-width:1100px; max-width:1200px;'>
      <div><a href='https://github.com/pkkid/django-searchquery'>
        <span class='icon'>search</span>
        <div class='title'>Django Searchquery</div>
        <p>Provides advanced search and filtering capabilities to structured data in Django models.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/python-plexapi'>
        <span class='icon'>data_object</span>
        <div class='title'>Python PlexAPI</div>
        <p>Python bindings for the Plex Server API. Navigate and manage your local or remote shared libraries.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pygrid'>
        <span class='icon'>dashboard</span>
        <div class='title'>PyGrid</div>
        <p>Easily organize open windows by tiling and positioning them to make the best use of your desktop.</p>
      </a></div>
      <div><a href='https://github.com/django-dbbackup/django-dbbackup'>
        <span class='icon'>database</span>
        <div class='title'>Django DBBackup</div>
        <p>Management commands to backup and restore project database to AmazonS3, Dropbox or Local Disk.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/link-manager'>
        <span class='icon'>linked_services</span>
        <div class='title'>Link Manager</div>
        <p>Collection of scripts to help easily sync specific configuration files across all your Linux computers.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pkmeter-conky'>
        <span class='icon'>speed</span>
        <div class='title'>PKMeter-Conky</div>
        <p>Collection of scripts and a Conky configuration. Makes fetching data easy and results stored as json.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pushingkarma'>
        <span class='icon'>public</span>
        <div class='title'>PushingKarma</div>
        <p>This websites Python, Django, and Vue source code freely available in the rare case someone finds it useful.</p>
      </a></div>
    </div>
  </article>
</template>

<script setup>

</script>

<style>
  #splash {
    position: relative;
    height: 100vh;

    .bgimg {
      background-color: #282828;
      background-image: url('/static/img/mountain_landscape.png');
      background-position: center center;
      background-size: cover;
      position: absolute;
      top: 0; left: 0;
      width: calc(100vw - var(--navwidth)); height: 100vh;
    }
    .content {
      align-items: center;
      backdrop-filter: grayscale(20%);
      background-color: #0002;
      display: flex;
      flex-direction: column;
      justify-content: center;
      position: absolute;
      top: 0; left: 0;
      width: calc(100vw - var(--navwidth)); height: 100vh;
    }
    .content:after {
      background: radial-gradient(ellipse at center, #0000 0%, #0005 80%, #0005 100%);
      content: '';
      display: block;
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
    }
    .photo {
      border-radius: 100%;
      border: 8px solid #665c54dd;
      width: 200px;
      margin-bottom: 38px;
    }
    .name {
      text-align: center;
      text-transform: uppercase;
      font-size: 3rem;
      font-family: "Merriweather", sans-serif;
      font-weight: 300;
      margin-bottom: 100px;
      color: #ebdbb2;
      span { color: #fe8019; }
    }
  }

  article {
    padding: 40px;
    font-family: "Merriweather", sans-serif;
    font-size: 18px;
    color: #504945;
    h1 {
      font-size: 40px;
      color: #3c3836;
      margin-bottom: 30px;
      .subtext {
        margin-top: -10px;
        font-size: 16px;
      }
      &:after {
        border-bottom: 2px solid #d65d0e;
        content: " ";
        display: block;
        height: 10px;
        width: 300px;
      }
    }
    h2 {
      font-size: 25px;
      .accent { color:#d65d0e; }
    }
    p { margin-top:15px; }
  }
  
  #about {
    .photowrap {
      display: flex;
      margin-top: 30px;
      .photo {
        border: 10px solid #282828;
        box-sizing: border-box;
        height: 300px;
        margin-top: 40px;
        margin-right: 80px;
        position: relative;
        top:-10px; left:20px;
        width: 400px;
        img {
          position: relative;
          width: 400px;
          top:-30px; left:-30px;
        }
      }
    }
  }

  #projects {
    .projectlist {
      display: grid;
      grid-template-columns: 30% 30% 30%;
      grid-gap: 30px;
      margin-top: 40px;
    }
    a {
      background-color: #fff;
      box-shadow: 0 0 20px #ccc;
      box-sizing: border-box;
      color: #504945;
      display: block;
      padding: 30px 40px 33px 40px;
      position: relative;
      text-decoration: none !important;
      top: 0px;
      transition: all .2s ease;

      .icon {
        font-size: 3rem;
        position: relative;
        left: -6px;
      }
      .title {
        color: #363636;
        font-size: 1.4rem;
        font-weight: 400;
        left: -1px;
        line-height: 1;
        margin: 12px 0px 16px 0px;
        position: relative;
      }
      p {
        font-size: 14px;
        font-weight: 400;
        height: 90px;
        letter-spacing: 0.5px;
        line-height: 1.7;
        word-wrap: break-word;
      }
      &:hover {
        top: -10px;
      }
    }
  }
</style>
