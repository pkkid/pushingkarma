<template>
  <div class='layoutpaper'>
    <article class='paper lightbg'>
      <slot name='content'>paper article</slot>
    </article>
    <div class='controls'>
      <slot name='controls'>controls</slot>
    </div>
  </div>
</template>

<style>
  .layoutpaper {
    align-items: flex-start;
    background-color: var(--lightbg-bg4);
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: center;
    min-height: calc(100vh - var(--navheight));

    .paper {
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 #4445, 0 1px 3px 1px #4442;
      min-height: 70vh;
      padding: 25px 30px 60px 30px;
      position: relative;
      width: 900px;
      margin: 30px 20px;
      ::selection { color:black; background:#ccc; }
    }
    .controls {
      border: 1px solid red;
      margin: 30px 20px 30px 0px;
    }
  }
  
</style>