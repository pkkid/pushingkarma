<template>
  <div id='logo'>
    <img class='logoimg' src='/static/img/pk.svg'/>
    <div class='logotxt'>PushingKarma</div>
  </div>
</template>

<style>
  :root {
    --bounce: cubic-bezier(.47,1.64,.41,.8);
  }
  .logoimg {
    position: absolute;
    z-index: 9;
    transition: all 0.5s var(--bounce);
  }
  .logotxt {
    color: #fbf1c7;
    font-family: var(--fontfamily-title);
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 3px;
    line-height: 30px;
    position: absolute;
    text-align: center;
    text-transform: uppercase;
    z-index: 9;
    transition: all 0.5s var(--bounce);
  }

  /* Left Navigation */
  body.leftnav {
    .logoimg {
      left: calc((300px - 130px) / 2);
      top: 50px;
      width: 130px;
    }
    .logotxt {
      top: 150px;
      left: 0px;
      width: 300px;
    }
  }

  /* Top Navigation */
  body.topnav {
    .logoimg {
      width: 61px;
      left: 20px;
      top: calc((60px - 40px) / 2);
    }
    .logotxt {
      top: 0px;
      left: 100px;
      line-height: 60px;
    }
  }
</style>
