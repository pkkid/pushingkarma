<template>
  <div id='search'>
    <div class='searchwrap'>
      <!-- Search Input -->
      <span id='search-icon' class='mdi mdi-magnify'></span>
      <input id='search-input' type='text' v-model='search' autofocus='true'
        spellcheck='false' autocomplete='off' ref='search'
        v-on:input='updateSearch'
        v-on:keydown.up.prevent='updateSelected(selected-1)'
        v-on:keydown.down.prevent='updateSelected(selected+1)'
        v-on:keyup.enter.prevent='updateNote'>
      <!-- Search Results -->
      <div id='search-results'>
        <div class='scrollwrap'>
        <div class='scrollbox'>
          <div class='result' v-for='(note, i) in notes.objects' v-bind:key='note.id'
            v-bind:class='{selected:i == selected}' @click='selected=i; updateNote()'>
            {{note.title}}
            <div class='subtext'>
              {{note.tags}} <span v-if='note.tags'>-</span>
              {{note.created | formatDate('MMM DD, YYYY')}}
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import {sync} from 'vuex-pathify';
  import {buildquery, minmax} from '@/utils/utils';
  import {isEqual, trim} from 'lodash';

  var QUERY_NOTES = `query {
    notes(search:{search}, page:{page}) {
      page numPages hasNext hasPrev
      objects { id slug title tags created }
    }}`;
  
  var QUERY_NOTE = `query {
    note(id:{id}) {
      id slug title body tags created 
    }}`;

  export default {
    name: 'Search',
    computed: { ...sync('notes/*') },
    
    data: () => ({
      request_search: null,
      request_note: null,
      selected: 0,
    }),

    created: function() {
      // Init function when this component is created.
      this.search = trim(this.search || this.$route.query.search || '');
      this.updateSearch(null, this.updateNote);
    },

    methods: {
      // Focus
      // Focus the search input
      focus: function(event) {
        if (event) event.preventDefault();
        this.$refs.search.select();
      },

      // Update History
      // Update the address bar history.
      updateHistory: function() {
        let query = {};
        if (this.search.length >= 1) { query.search = this.search; }
        if (this.note.id) { query.id = this.note.id; }
        if (!isEqual(query, this.$router.history.current.query)) {
          this.$router.push({query});
        }
      },

      // Update Note
      // Update the selected note.
      updateNote: function(event, callback) {
        let self = this;
        let i = this.selected;
        let noteid = this.notes.objects[i].id;
        this.$refs.search.focus();
        if (this.request_note) { this.request_note.cancel(); }
        this.request_note = buildquery(QUERY_NOTE, {id:noteid});
        this.request_note.xhr.then(function(response) {
          self.note = response.data.data.note;
          self.editor.setContent(self.note.body);
          self.updateHistory();
          self.$refs.search.blur();
          if (callback) { callback(); }
        });
      },

      // Update Search
      // Update the list of notes to display.
      updateSearch: function(event, callback) {
        let self = this;
        if (this.request_search) { this.request_search.cancel(); }
        this.request_search = buildquery(QUERY_NOTES, {search:self.search, page:1});
        this.request_search.xhr.then(function(response) {
          self.notes = response.data.data.notes;
          self.selected = 0;
          self.updateHistory();
          if ((self.notes.objects.length) && (callback)) { callback(); }
        });
      },

      // Update Selected
      // Update the selected value.
      updateSelected(index) {
        this.selected = minmax(index, 0, this.notes.objects.length-1);
      },
    },

  };
</script>

<style lang='scss'>
  // Search Input
  #search {
    position: fixed;
    top: 60px;
    .searchwrap { position: relative; }
  }
  #search-input {
    background-color: darken($darkbg-color, 5%);
    border-bottom: 1px solid rgba(0, 0, 0, 0.2);
    border-width: 0px;
    color: $darkbg-input;
    font-size: 0.9em;
    font-weight: 500;
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
    font-size: 1.2em;
    left: 10px;
    line-height: 40px;
    position: absolute;
    z-index: 1;
  }
  #search-results {
    position: fixed;
    top: 100px;
    .result {
      border-bottom-right-radius: 8px;
      border-left: 3px solid transparent;
      border-top-right-radius: 8px;
      color: $darkbg-text;
      cursor: pointer;
      font-size: 0.85em;
      font-weight: 500;
      overflow: hidden;
      padding: 15px 15px 15px 12px;
      text-overflow: ellipsis;
      white-space: nowrap;
      width: 290px;
      &.selected,
      &:hover {
        border-left: 3px solid $darkbg-accent;
        background-color: lighten($darkbg-color, 5%);
      }
    }
    .subtext {
      font-size: 0.7em;
      font-weight: 400;
      color: $darkbg-text-dim;
      padding-top: 2px;
    }
    .scrollwrap {
      position: relative;
      .scrollbox {
        overflow-x: hidden;
        overflow-y: scroll;
        height: calc(100vh - 100px);
        &::-webkit-scrollbar { width:10px; }
        &::-webkit-scrollbar-thumb {
          background: lighten($darkbg-color, 40%);
          border-radius: 5px;
          border: 2px solid $darkbg-color;
        }
        &:before {
          content: ' ';
          background-color: $darkbg-color;
          height: 100%;
          opacity: 1;
          position: absolute;
          right: 0;
          top: 0;
          transition: all .5s ease;
          width: 10px;
        }
      }
      &:hover .scrollbox:before { opacity:0; width:0px; right:5px;}
    }
  }
</style>
