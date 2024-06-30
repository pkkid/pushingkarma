<template>
  <div id='splash'>
    <div class='bgimg'/>
    <div class='content'>
      <img class='photo' src='/static/img/photo.jpg'>
      <div class='name'>Michael <span>Shepanski</span></div>
    </div>
  </div>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
  Home View<br/><br/><br/>
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
      width: calc(100vw - 300px); height: 100vh;
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
      width: calc(100vw - 300px); height: 100vh;
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
</style>
