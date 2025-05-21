<template>
  <div id='newtab'>
    <div class='logoimg'/>
    <div class='logotxt'>PushingKarma</div>
  </div>
</template>

<style>
  #newtab {
    background: url('/static/img/floral-pattern.jpg') no-repeat center center fixed;
    background-size: cover;
    height: 100vh;
    width: 100vw;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

    .logoimg {
      mask: url('/static/img/pk.svg') no-repeat center/contain;
      width: 10%;
      aspect-ratio: 1;
      background-color: color-mix(in srgb, var(--darkbg-fg1), #000 20%);
    }
    .logotxt {
      color: var(--darkbg-fg1);
      font-family: var(--fontfamily-title);
      font-size: 1.2vw;
      font-weight: 700;
      letter-spacing: 3px;
      line-height: 30px;
      margin-top: -0.8vw;
      text-align: center;
      text-transform: uppercase;
    }
  }
</style>
