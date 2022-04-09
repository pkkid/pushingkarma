<!--
Page Wrap
Simple Layout that looks like a page (or a peice of paper).
-->
<template>
  <div id='pagewrap'>
    <div id='page'>
      <article><slot>#page article</slot></article>
    </div>
  </div>
</template>

<style lang='scss'>
  #pagewrap {
    border: 2px solid transparent;
  }
  #page {
    background-color: $lightbg-bg1;
    border-radius: 2px;
    border: 1px solid darken($lightbg-bg3, 10%);
    box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
    color: $lightbg-text;
    font-family: $fontfamily-article;
    margin: 0px auto;
    max-width: 900px;
    min-height: 70vh;
    min-width: 900px;
    padding: 25px 30px;
    position: relative;
    ::selection { color:black; background:#ccc; }
  }
</style>
