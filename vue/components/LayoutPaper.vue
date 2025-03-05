<template>
  <div class='layoutpaper'>
    <article class='paper lightbg' :style="{width:`${props.width}px`}">
      <slot name='content'>paper article</slot>
    </article>
    <div class='controls' v-if='$slots.controls'>
      <div class='controls-fixed'>
        <slot name='controls'>controls</slot>
      </div>
    </div>
  </div>
</template>

<script setup>
  const props = defineProps({
    width: {type:Number, default:900},
  })
</script>

<style>
  .layoutpaper {
    align-items: flex-start;
    background-color: var(--lightbg-bg4);
    box-shadow: inset 0 0 5em 1em rgba(40, 40, 40, 0.15);
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
      /* width: 900px; */
      margin: 30px 20px;
      ::selection { color:black; background:#ccc; }
    }
    .controls {
      margin: 30px 20px 30px 0px;
      font-size: 16px;
      width: 250px;
      &:has(.controls-fixed:empty) { display: none; }
      .controls-fixed {
        position: fixed;
        width: 250px;
      }
      h2 {
        color: var(--lightbg-fg0);
        font-size: 18px;
        margin-bottom: 10px;
        margin-top: 40px;
      }
      .submenu {
        --linkcolor: var(--lightbg-text);
        --linkhover: var(--lightbg-blue1);
        --linkhoverunderline: 2px dotted var(--lightbg-blue1);
        border-left: 3px solid var(--lightbg-blue1);
        font-size: 13px;
        padding-left: 10px;
        position: relative;
      }
      a, a:visited {
        display: inline-block;
        line-height: 1.2;
        max-width: calc(100% - 10px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
</style>