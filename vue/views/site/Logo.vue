<template>
  <div id='logo'>
    <div class='logoimg' src='/static/img/pk.svg'/>
    <div class='logotxt'>PushingKarma</div>
  </div>
</template>

<style>
  :root {
    --bounce: cubic-bezier(.47,1.64,.41,.8);
  }
  #logo {
    .logoimg {
      aspect-ratio: 1.4;
      background-color: var(--darkbg-fg1);
      mask: url('/static/img/pk.svg') no-repeat center/contain;
      position: absolute;
      transition: all 0.5s var(--bounce);
      z-index: 9;
    }
    .logotxt {
      color: var(--darkbg-fg1);
      font-family: var(--fontfamily-title);
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 3px;
      line-height: 30px;
      position: absolute;
      text-align: center;
      text-transform: uppercase;
      transition: all 0.5s var(--bounce);
      z-index: 9;
    }
  }
  /* Left Navigation */
  body.leftnav {
    #logo .logoimg {
      left: calc((300px - 130px) / 2);
      top: 50px;
      width: 130px;
    }
    #logo .logotxt {
      top: 150px;
      left: 0px;
      width: 300px;
    }
  }

  /* Top Navigation */
  body.topnav {
    #logo .logoimg {
      width: 61px;
      left: 20px;
      top: calc((60px - 40px) / 2);
    }
    #logo .logotxt {
      top: 0px;
      left: 100px;
      line-height: 60px;
    }
  }
</style>
