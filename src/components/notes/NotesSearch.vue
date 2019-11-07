<template>
  <div id='search'>
    <div class='searchwrap'>
      <!-- Search Input -->
      <span id='search-icon' class='mdi mdi-magnify'></span>
      <input id='search-input' type='text' v-model='search' autofocus='true'
        spellcheck='false' autocomplete='off' ref='search'
        @keydown.up.prevent='setHighlighted(-1)'
        @keydown.down.prevent='setHighlighted(+1)'
        @keyup.enter.prevent='selected=highlighted'
        @keydown.esc.stop='$refs.search.blur()'>
      <!-- Search Results -->
      <div id='search-results'>
        <div class='scrollwrap'>
        <div class='scrollbox'>
          <div class='submenuitem' v-for='note in notes' :noteid='note.id' v-bind:key='note.id'
            v-bind:class='{highlighted:note.id == highlighted}' @click='selected=note.id'>
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
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  import Vue from 'vue';

  export default {
    name: 'NotesSearch',
    data: () => ({
      cancelSearch: null,  // Cancel search token
      highlighted: null,   // Highlighed note id
      notes: [],           // List of search results
      selected: null,      // Selected note id
      search: null,        // Current search string
    }),
    watch: { 
      // Watch Highlighted
      // Make sure item is visible
      highlighted: async function() {
        await Vue.nextTick();
        var container = document.querySelector('#search-results .scrollbox');
        var item = document.querySelector(`#search-results .submenuitem[noteid='${this.highlighted}']`);
        if (item) { utils.keepInView(container, item, 50, 'auto'); }
      },
      
      // Watch Search
      // Update results, history, and highlighted item.
      search: async function() {
        this.cancelSearch = api.cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var {data} = await api.NotesAPI.listNotes({search:this.search}, token);
          this.notes = data.results;
          this.highlighted = this.selected || this.notes[0].id;
          this.selected = this.selected ? this.selected : this.highlighted;
          utils.updateHistory(this.$router, {search:this.search});
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
      },

      // Watch selected
      // Update highlighted, history, focus, and emit event
      selected: function(selected) {
        this.highlighted = selected;
        utils.updateHistory(this.$router, {noteid:this.selected});
        this.$refs.search.focus();
        this.$emit('newSelection', selected);
      },
    },

    created: async function() {
      // Init function when this component is created.
      var noteid = this.$route.query.noteid;
      this.selected  = noteid ? parseInt(noteid) : null;
      this.search = _.trim(this.search || this.$route.query.search || '');
    },

    methods: {
      // Focus
      // Focus the search input
      focus: function(event) {
        if (event) event.preventDefault();
        this.$refs.search.select();
      },

      // Set Highlighted
      // Adjust highlighted by offset (for next / prev selection).
      setHighlighted: function(offset) {
        var index = utils.findIndex(this.notes, 'id', this.highlighted);
        var newIndex = utils.keepInRange(index+offset, 0, this.notes.length-1);
        this.highlighted = this.notes[newIndex].id;
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
