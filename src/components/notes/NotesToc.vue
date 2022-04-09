<template>
  <div id='toc'>
    <h2 style='margin-top:35px;'>Table of Contents</h2>
    <div class='submenu'>
      <div v-for='item in tocitems' v-bind:key='item.text' :class='item.type'>
        <router-link :to='{hash:item.slug, query:$route.query}'>{{item.text}}</router-link>
      </div>
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
            if (item.content === undefined) { continue; }
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
  #toc .submenu {
    .h1 { padding-left:0px; }
    .h2 { padding-left:0px; }
    .h3 { padding-left:15px; }
  }
</style>
