<template>
  <div id='search' class='darkbg'>
    <div class='searchwrap'>
      <!-- Search Input -->
      <b-icon class='searchicon' icon='magnify'/>
      <input class='searchinput' type='text' v-model='search' autofocus='true'
        spellcheck='false' autocomplete='off' ref='search'
        @keydown.up.prevent='setHighlighted(-1)'
        @keydown.down.prevent='setHighlighted(+1)'
        @keyup.enter.prevent='$emit("newSelection", highlighted)'
        @keydown.esc.stop='$refs.search.blur()'/>
      <!-- Search Results -->
      <div class='results'>
        <ScrollBox>
          <div class='result' v-for='note in notes' :key='note.id' :noteid='note.id'
            :class='{highlighted:note.id == highlighted}' @click='$emit("newSelection", note.id)'>
            {{note.title}}
            <div class='subtext'>
              {{note.tags}} <span v-if='note.tags'>-</span>
              {{note.created | formatDate('MMM DD, YYYY')}}
              <i v-if='isPrivateNote(note)' class='mdi mdi-key lock'/>
            </div>
          </div>
          <div v-if='!notes.length' class='empty'>No items to display.</div>
        </ScrollBox>
      </div>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import NotesMixin from './NotesMixin';
  import ScrollBox from '@/components/ScrollBox';
  import trim from 'lodash/trim';
  import Vue from 'vue';

  export default {
    name: 'NotesSearch',
    mixins: [NotesMixin],
    components: {ScrollBox},
    data: () => ({
      cancelSearch: null,  // Cancel search token
      highlighted: null,   // Highlighed note id
      notes: [],           // List of search results
      search: null,        // Current search string
    }),
    computed: {
      noteid: pathify.get('notes/note@id'),
    },
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
        this.updateResults();
      },

      // Watch Note ID
      // Update highlighted, history, focus.
      noteid: function(noteid) {
        console.log(`New Note Id: ${noteid}`);
        this.highlighted = noteid;
        utils.updateHistory(this.$router, {noteid});
        this.$refs.search.focus();
      },
    },

    // Created
    // Initialize noteid and search from URL
    mounted: function() {
      var noteid = this.$route.query.noteid;
      if (noteid) { this.$emit('newSelection', noteid); }
      this.search = trim(this.search || this.$route.query.search || '');
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

      // Update Results
      // Update the result listing in the side bar
      updateResults: async function() {
        this.cancelSearch = api.cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var {data} = await api.Notes.getNotes({search:this.search}, token);
          this.notes = data.results;
          this.highlighted = this.noteid || this.notes[0].id;
          if (!this.noteid) { this.$emit('newSelection', this.highlighted); }
          utils.updateHistory(this.$router, {search:this.search});
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
      },

    },
  };
</script>

<style lang='scss'>
  #notes #search {
    opacity: 0.6;
    transition: opacity 1s ease;
    position: fixed;
    top: 60px;
    &:hover, &:focus,
    &:focus-within { opacity: 1; }

    .searchinput {
      background-color: darken($darkbg-color, 5%);
      border-bottom: 1px solid rgba(0, 0, 0, 0.2);
      border-width: 0px;
      color: $darkbg-input;
      font-size: 0.9rem;
      font-weight: 500;
      height: 40px;
      line-height: 40px;
      padding: 0px 10px 0px 45px;
      position: relative;
      width: 300px;
      &:focus {
        border-width: 0px;
        outline: none;
      }
    }
    .searchicon {
      left: 10px;
      opacity: 0.7;
      position: absolute;
      top: 8px;
      z-index: 1;
    }
    .result {
      border-bottom-right-radius: 8px;
      border-left: 3px solid transparent;
      border-top-right-radius: 8px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      overflow: hidden;
      padding: 13px 15px 13px 12px;
      text-overflow: ellipsis;
      user-select: none;
      white-space: nowrap;
      opacity: 0.8;
      &.highlighted,
      &:hover {
        border-left: 3px solid $darkbg-accent;
        background-color: lighten($darkbg-color, 5%);
      }
      .subtext {
        font-size: 0.8em;
        font-weight: 400;
        color: $darkbg-text-dim;
        padding-top: 2px;
      }
      .lock {
        font-size: 1.2em !important;
        margin-left: 3px;
        margin-top: 1px;
      }
    }
    .empty {
      font-size: 0.8rem;
      font-weight: 500;
      margin: 30px auto;
      opacity: 0.8;
      text-align: center;
    }
  }
</style>
