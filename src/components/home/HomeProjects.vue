<template>
  <div id='projects' class='parallax-static'>
    <h3>Projects <span>Whats been keeping me busy</span></h3>
    <ul class='projectlist'>
      <li><a href='https://github.com/mjs7231/python-plexapi'>
        <i class='mdi mdi-code-braces'></i>
        <div class='title'>Python PlexAPI</div>
        <p>Python bindings for the Plex Server API. Navigate and manage your local or remote shared libraries.</p>
      </a></li>
      <li><a href='https://github.com/mjs7231/pygrid'>
        <i class='mdi mdi-view-grid'></i>
        <div class='title'>PyGrid</div>
        <p>Easily organize open windows by tiling and positioning them to make the best use of your desktop.</p>
      </a></li>
      <li><a href='https://github.com/django-dbbackup/django-dbbackup'>
        <i class='mdi mdi-database'></i>
        <div class='title'>Django DBBackup</div>
        <p>Management commands to backup and restore project database to AmazonS3, Dropbox or Local Disk.</p>
      </a></li>
      <li><a href='https://github.com/pkkid/link-manager'>
        <i class='mdi mdi-link'></i>
        <div class='title'>Link Manager</div>
        <p>Collection of scripts to help easily sync specific configuration files across all your Linux computers.</p>
      </a></li>
      <li><a href='https://github.com/pkkid/pkmeter-conky'>
        <i class='mdi mdi-speedometer'></i>
        <div class='title'>PKMeter-Conky</div>
        <p>Collection of scripts and a Conky configuration. Makes fetching data easy and results stored as json.</p>
      </a></li>
      <li><a href='https://github.com/pkkid/pushingkarma'>
        <i class='mdi mdi-earth'></i>
        <div class='title'>PushingKarma</div>
        <p>This websites Python, Django, and Vue source code freely available in the rare case someone finds it useful.</p>
      </a></li>
      <!-- <li><a href='https://bitbucket.org/mjs7231/pks-movie-database/src'>
        <i class='mdi mdi-movie'></i>
        <div class='title'>PKs Movie Database</div>
        <p>PHP app to publish and browse an Ant Movie Database. This gained popularity a few years back.</p>
      </a></li> -->
      <div style='clear:both;'></div>
    </ul>
  </div>
</template>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  .projectlist {
    padding: 0px;
    margin: 75px 0px 0px -30px;
    list-style-type: none;
    a {
      box-shadow: 0 0 20px rgba(0,0,0,.1);
      box-sizing: border-box;
      color: $dark-bgh;
      display: block;
      float: left;
      margin-bottom: 30px;
      margin-left: 30px;
      padding: 40px 40px 33px 40px;
      position: relative;
      text-decoration: none;
      top: 0px;
      transition: all .2s ease-out;
      width: 30%;
      min-width: 310px;
      .mdi {
        font-size: 55px;
        position: relative;
        left: -6px;
      }
      .title {
        font-family: "Montserrat";
        font-size: 22px;
        font-weight: 600;
        line-height: 1;
        margin: 15px 0px 18px 0px;
        position: relative;
        left: -1px;
      }
      p {
        font-size: 14px;
        line-height: 1.8;
        letter-spacing: 0.5px;
        word-wrap: break-word;
        font-weight: 400;
        height: 75px;
      }
      &:hover {
        top: -10px;
      }
    }
  }

</style>
