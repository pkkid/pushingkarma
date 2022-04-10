<template>
  <div id='meta' v-if='tags.length'>
    <div>Published on {{note.created | formatDate('MMM DD, YYYY')}}.</div>
    <div>Updated on {{note.modified | formatDate('MMM DD, YYYY')}}.</div>
    <div v-if='tags.length'>
      Tags: <a v-for='tag in tags' v-bind:key='tag' @click='click(tag)'>{{tag}}</a>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NotesTags',
    props: {
      note: Object,
      tagstr: String,
      search: Object,
    },       
    data: () => ({
      tags: [],
    }),   
    watch: {
      tagstr: function() {
        let tags = this.tagstr.toLowerCase().split(' ');
        this.tags = tags.filter(tag => tag.length);
      },
    },
    methods: {
      click: function(tag) {
        this.search.search = tag;
        this.search.focus();
      }
    }
  };
</script>

<style lang='scss'>
  #meta {
    font-size: 0.9em;
    margin-top: 40px;
    a { margin-right: 5px; }
  }
</style>
