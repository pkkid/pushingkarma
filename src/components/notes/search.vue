<template>
  <div id='search'>
    <span id='search-icon' class='mdi mdi-magnify'></span>
    <input id='search-input' type='text' v-model='search' v-on:input='updateSearch'
      autofocus='true' spellcheck='false' autocomplete='off'>
  </div>
</template>

<script>
  import router from '@/router'
  import axios from 'axios'
  import {sync} from 'vuex-pathify'

  export default {
    name: 'Search',
    data: function() { return {
      cancelxhr: null,
    }},
    computed: {
      search: sync('notes_search'),
      list: sync('notes_list'),
    },

    created: function() {
      this.$store.set('notes_search', this.$route.query.search)
    },

    methods: {
      updateSearch: function() {
        let self = this
        this.cancelSearch()
        this.cancelxhr = axios.CancelToken.source()
        axios.post('/graphql?', {
          query: `query { note(id:29) { id title slug }}`,
          variables: null
        },{
          cancelToken: this.cancelxhr.token
        }).then(function(response) {
          console.log(response)
          router.push({path:'/notes', query:{search:self.search}})
        }).catch(function(error) {
          console.log(error)
        })
      },

      cancelSearch: function() {
        if (this.cancelxhr) { this.cancelxhr.cancel('Starting new search..') }
      },
    }
  }
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
