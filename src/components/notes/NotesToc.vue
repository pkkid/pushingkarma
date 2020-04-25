<template>
  <div id='toc'>
    <div v-for='item in tocitems' v-bind:key='item.text' :class='item.type'>
      <router-link :to='{hash:item.slug, query:$route.query}'>{{item.text}}</router-link>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NotesToc',
    props: {
      title: String,                // Article title
      content: Array,               // Editor.getJSON().content object
    },       
    data: () => ({tocitems: []}),   // Toc items to display
    watch: {
      content: function() {
        let tocitems = [{text:this.title, slug:'#title', type:'h1'}];
        for (let item of this.content) {
          if (item.type == 'heading') {
            var text = item.content[0].text;
            tocitems.push({
              text: text,
              slug: '#'+ text.toLowerCase().replace(/\s/g, '_'),
              type: 'h'+ item.attrs.level,
            });
        }}
        this.tocitems = tocitems;
      },
    },
  };
</script>

<style lang='scss'>
  #toc {
    border-left: 3px solid $lightbg-blue1;
    font-family: $fontfamily-article;
    font-weight: 400;
    padding-left: 10px;
    .h1 { font-weight:bold; color:darken($lightbg-text, 30%); }
    .h2 { padding-left:0px; }
    .h3 { padding-left:15px; }
    a {
      color: $lightbg-text;
      &:hover { color:$lightbg-link; text-decoration:none; }
    }
  }
</style>
