<template>
  <div id='tags' v-if='tags.length'>
    <h2>Note Tags</h2>
    <div class='submenu'>
      <template v-for='tag in tags'>
        <a v-bind:key='tag' @click='click(tag)'>{{tag}}</a>
      </template>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NotesTags',
    props: {
      tagstr: String,
      search: null,
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
