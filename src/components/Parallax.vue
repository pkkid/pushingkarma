<!--
Parallax Wrapper - Provides the SCSS to add parallax to a layout. You'll want
to use one of the two layout wrappers below:
  .parallax-bg -- A moving background image.
  .parallax-static -- Static content (not moving).

Example Template:
  <Parallax>
    <div id='bgimg' class='parallax-bg'></div>
    <div class='parallax-static'>Hi Mom!</div>
  </Parallax>

Set the Background Image URL
  #bgimg::after { background-image: url('example.jpg'); }
-->
<template>
  <div class='parallax-wrapper'>
    <slot/>
  </div>
</template>

<style lang='scss'>
  .parallax-wrapper {
    height: 100vh;
    overflow-x: hidden;
    overflow-y: auto;
    perspective: 2px;
    scroll-behavior: smooth;

    .parallax-bg {
      height: 100vh;
      position: relative;
      &::after {
        content: " ";
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: -3px;
        transform: translateZ(-2px) scale(2.01);
        background-size: cover;
        background-position-x: 50%;
        background-position-y: 50%;
        z-index: -1;
      }
    }

    .parallax-static {
      background-color: $lightbg-bg1;
      color: #282828;
      padding: 40px 40px 100px 40px;
      position: relative;
      text-align: left;
    }
  }
</style>
