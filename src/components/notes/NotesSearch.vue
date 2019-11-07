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
          <div class='submenuitem' v-for='(note, i) in notes' v-bind:key='note.id'
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
  import Vue from 'vue';
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
      await this.updateSearch(id, {behavior:'auto'});
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
      updateSearch: async function(id, opts) {
        this.cancelSearch = cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var {data} = await NotesAPI.listNotes({search:this.search}, token);
          var highlighted = id === undefined ? {i:0} : {id:id};
          opts = Object.assign({}, highlighted, opts);
          this.notes = data.results;
          this.setHighlighted(opts);
          this.updateHistory({search:this.search});
        } catch(err) {
          if (!isCancel(err)) { throw(err); }
        }
      },

      // Update highlighted
      // Update the highlighted value.
      async setHighlighted(opts) {
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
        await Vue.nextTick();
        var behavior = opts.behavior || 'smooth';
        var container = document.querySelector('#search-results .scrollbox');
        var item = document.querySelector(`#search-results .submenuitem:nth-child(${this.highlighted+1})`);
        container.scroll({top:item.offsetTop-100, behavior:behavior});
      },

    },
  };
</script>

<style lang='scss'>
  #notes {
    #sidebar .submenuitem {
      padding-top: 15px;
      padding-bottom: 15px;
    }
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
      font-size: 1.4rem;
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
      font-size: 1.9rem;
      left: 10px;
      line-height: 40px;
      position: absolute;
      z-index: 1;
    }
    #search-results {
      position: fixed;
      top: 100px;
    }
  }
</style>
