<template>
  <div id='search'>
    <span id='search-icon' class='mdi mdi-magnify'></span>
    <input id='search-input' type='text' v-model='search' v-on:input='updateSearch'
      autofocus='true' spellcheck='false' autocomplete='off'>
  </div>
</template>

<script>
  import router from '@/router';
  import {sync} from 'vuex-pathify';
  import {query} from '@/pk/utils';

  var QUERY_NOTES = `query {
    notes(search:"{search}", page:{page}) {
      page numPages hasNext hasPrev
      objects { id slug title tags }
    }}`;

  export default {
    name: 'Search',
    data: function() { return { request: null }; },
    computed: { ...sync('notes/*') },
    created: function() { this.$store.set('notes/search', this.$route.query.search); },
    methods: {
      
      /** Update Search - Update the list of notes to display */
      updateSearch: function() {
        let self = this;
        if (self.search.length < 3) { return; }
        if (this.request) { this.request.cancel(); }
        this.request = query(QUERY_NOTES, {search:self.search, page:1});
        this.request.xhr.then(function(response) {
          router.push({path:'/notes', query:{search:self.search}});
          self.list = response.data;
        });
      },

    }
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  // Search Input
  #search-input {
    background-color: $dark-bgh;
    border-bottom: 1px solid rgba(0, 0, 0, 0.2);
    border-width: 0px;
    color: $light-yellow0;
    font-size: 20px;
    height: 40px;
    line-height: 40px;
    padding: 0px 10px 0px 40px;
    position: relative;
    width: 300px;
    &:focus {
      border-width: 0px;
      outline: none;
    }
  }
  #search-icon {
    font-size: 20px;
    left: 10px;
    line-height: 40px;
    position: absolute;
    top: 0px;
    z-index: 1;
  }
</style>
