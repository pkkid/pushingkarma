<!--
Page Wrap
Simple Layout that looks like a page (or a peice of paper).
-->
<template>
  <div id='pagewrap'>
    <div id='page' :style='{width,padding}'>
      <article><slot>#page article</slot></article>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'PageWrap',
    props: {
      width: {type:String, default:'900px'},
      padding: {type:String, default:'40px 50px'},
    },
  };
</script>

<style lang='scss'>
  #page {
    background-color: $lightbg-bg1;
    border-radius: 2px;
    border: 1px solid darken($lightbg-bg3, 10%);
    box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
    color: $lightbg-text;
    font-family: $fontfamily-article;
    min-height: calc(70vh);
  }
</style>
