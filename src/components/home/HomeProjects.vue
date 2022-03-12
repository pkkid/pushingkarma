<template>
  <article id='projects' class='parallax-static'>
    <h1>Projects <div class='subtext'>Whats been keeping me busy</div></h1>
    <div class='projectlist'>
      <div><a href='https://github.com/pkkid/python-plexapi'>
        <i class='mdi mdi-code-braces'></i>
        <div class='title'>Python PlexAPI</div>
        <p>Python bindings for the Plex Server API. Navigate and manage your local or remote shared libraries.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pygrid'>
        <i class='mdi mdi-view-grid'></i>
        <div class='title'>PyGrid</div>
        <p>Easily organize open windows by tiling and positioning them to make the best use of your desktop.</p>
      </a></div>
      <div><a href='https://github.com/django-dbbackup/django-dbbackup'>
        <i class='mdi mdi-database'></i>
        <div class='title'>Django DBBackup</div>
        <p>Management commands to backup and restore project database to AmazonS3, Dropbox or Local Disk.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/link-manager'>
        <i class='mdi mdi-link'></i>
        <div class='title'>Link Manager</div>
        <p>Collection of scripts to help easily sync specific configuration files across all your Linux computers.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pkmeter-conky'>
        <i class='mdi mdi-speedometer'></i>
        <div class='title'>PKMeter-Conky</div>
        <p>Collection of scripts and a Conky configuration. Makes fetching data easy and results stored as json.</p>
      </a></div>
      <div><a href='https://github.com/pkkid/pushingkarma'>
        <i class='mdi mdi-earth'></i>
        <div class='title'>PushingKarma</div>
        <p>This websites Python, Django, and Vue source code freely available in the rare case someone finds it useful.</p>
      </a></div>
      <div style='clear:both;'></div>
    </div>
  </article>
</template>

<style lang='scss'>
  #home .projectlist {
    padding: 0px;
    margin: 75px 0px 0px -30px;
    list-style-type: none;
    a {
      box-shadow: 0 0 20px rgba(0,0,0,.1);
      box-sizing: border-box;
      color: $lightbg-text;
      display: block;
      float: left;
      margin-bottom: 30px;
      margin-left: 30px;
      min-width: 310px;
      padding: 40px 40px 33px 40px;
      position: relative;
      text-decoration: none !important;
      top: 0px;
      transition: all .2s ease-out;
      width: 30%;

      .mdi {
        font-size: 3rem;
        position: relative;
        left: -6px;
      }
      .title {
        font-size: 1.4rem;
        font-weight: 400;
        left: -1px;
        line-height: 1;
        margin: 15px 0px 18px 0px;
        position: relative;
      }
      p {
        font-size: 1rem;
        font-weight: 400;
        height: 75px;
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
