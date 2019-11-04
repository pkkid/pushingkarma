<template>
  <div id='search'>
    <div class='searchwrap'>
      <!-- Search Input -->
      <span id='search-icon' class='mdi mdi-magnify'></span>
      <input id='search-input' type='text' v-model='search' autofocus='true'
        spellcheck='false' autocomplete='off' ref='search'
        @input='updateSearch()'
        @keydown.up.prevent='setHighlighted({i:highlighted-1})'
        @keydown.down.prevent='setHighlighted({i:highlighted+1})'
        @keyup.enter.prevent='updateSelection'
        @keydown.esc.stop='$refs.search.blur()'>
      <!-- Search Results -->
      <div id='search-results'>
        <div class='scrollwrap'>
        <div class='scrollbox'>
          <div class='result' v-for='(note, i) in notes' v-bind:key='note.id'
            v-bind:class='{highlighted:i == highlighted}' @click='highlighted=i; updateSelection()'>
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
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import {isEqual, trim, pickBy, identity} from 'lodash';
  import {cancel, isCancel, NotesAPI} from '@/api';

  export default {
    name: 'NotesSearch',
    computed: {
      editor: pathify.sync('notes/editor'),
      note: pathify.sync('notes/note'),
      notes: pathify.sync('notes/notes'),
    },
    data: () => ({
      cancelSearch: null,
      highlighted: 0,
    }),

    created: async function() {
      // Init function when this component is created.
      var id = parseInt(this.$route.query.id);
      this.search = trim(this.search || this.$route.query.search || '');
      await this.updateSearch(id);
      this.updateSelection();
      this.$refs.search.focus();
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
      updateHistory: function(changes) {
        var query = Object.assign({}, this.$router.history.current.query, changes);
        query = pickBy(query, identity);  // remove falsey values
        if (!isEqual(query, this.$router.history.current.query)) {
          this.$router.push({query});
        }
      },

      // UpdateSelection
      // Update the selected note
      updateSelection: function() {
        let i = this.highlighted;
        let noteid = this.notes[i].id;
        this.updateHistory({id:noteid.toString()});
        this.$refs.search.focus();
        this.$emit('newSelection', noteid);
      },

      // Update Search
      // Update the list of notes to display.
      updateSearch: async function(id) {
        this.cancelSearch = cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var {data} = await NotesAPI.listNotes({search:this.search}, token);
          this.notes = data.results;
          this.setHighlighted(id === undefined ? {i:0} : {id:id});
          this.updateHistory({search:this.search});
        } catch(err) {
          if (!isCancel(err)) { throw(err); }
        }
      },

      // Update highlighted
      // Update the highlighted value.
      setHighlighted(opts) {
        // Update highlighted item by index or noteid
        if (opts.i !== undefined) {
          this.highlighted = utils.keepInRange(opts.i, 0, this.notes.length-1);
        } else if (opts.id !== undefined) {
          for (var i=0; i<this.notes.length; i++) {
            if (opts.id == this.notes[i].id) {
              this.highlighted = i;
            }
          }
        }
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
      &.highlighted,
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
