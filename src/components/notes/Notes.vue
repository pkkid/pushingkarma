<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <SidePanel>
      <template v-slot:sidepanel>
        <Search ref='search' @newSelection='updateNote'/>
      </template>
      <template v-slot:contentarea>
        <div id='notewrap'>
          <!-- Edit Menu & Note -->
          <PageWrap>
            <NotesEditMenu ref='editmenu'/>
            <h1><input name='title' autocomplete='off' placeholder='Enter a Title' v-model='note.title' :readonly=!editing />
              <div class='subtext'>
                {{note.created | formatDate('MMM DD, YYYY')}} - 
                <input name='tags' placeholder='tags' autocomplete='off' v-model='note.tags' :readonly=!editing />
              </div>
            </h1>
            <editor-content id='editor' :editor='editor' />
          </PageWrap>
          <!-- Table of Contents & Edit Controls -->
          <div id='rightmenu'>
            <NotesToc :title='title' :content='content'/>
            <div class='controls' if='userid !== null'>
              <div v-if='editing'><i class='mdi mdi-cancel'/> <a @click='editing=false'>Cancel Changes</a></div>
              <div v-else-if='userid'>
                <i class='mdi mdi-pencil-outline'/> <a @click='editing=true'>Edit Note</a><br/>
                <i class='mdi mdi-file-plus-outline'/> <a @click='createNote(note)'>Create Note</a><br/>
                <i class='mdi mdi-delete'/> <a @click='deleteNote(note)'>Delete Note</a>
              </div>
            </div>
          </div>
          <div style='clear:left;'/>
        </div>
      </template>
    </SidePanel>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import Navigation from '@/components/site/Navigation';
  import SidePanel from '@/components/site/SidePanel';
  import PageWrap from '@/components/site/PageWrap';
  import NotesEditMenu from './NotesEditMenu';
  import NotesToc from './NotesToc';
  import Search from './NotesSearch';
  import {Editor, EditorContent} from 'tiptap';

  export default {
    name: 'Notes',
    components: {Navigation, SidePanel, PageWrap, NotesEditMenu, NotesToc, Search, EditorContent},
    computed: {
      editing: pathify.sync('notes/editing'),
      editor: pathify.sync('notes/editor'),
      note: pathify.sync('notes/note'),
      title: pathify.sync('notes/note@title'),
      userid: pathify.get('global/user@id'),
      content: function() { return this.editor ? this.editor.getJSON().content : []; },
      keymap: function() { return {
        'f1': (event) => this.$refs.search.focus(event),
        'e': (event) => this.$refs.editmenu.startEditing(event),
        'ctrl+s': (event) => this.$refs.editmenu.save(event),
        'esc': (event) => this.$refs.editmenu.stopEditing(event),
      };},
    },
    mounted: function() {
      // Tiptap Examples: https://github.com/scrumpy/tiptap
      // Tiptap Documentation: https://tiptap.scrumpy.io/docs
      this.editor = new Editor({
        editable: false,
        onUpdate: this.updateToc,
        extensions: this.$refs.editmenu.extensions(),
      });
    },
    methods: {

      // Create Note
      // Create and start editing a new note
      createNote: async function() {
        var params = {title:'New Note', body:'--'};
        var {data} = await api.Notes.createNote(params);
        this.$refs.search.updateResults();
        this.updateNote(data.id);
      },

      // Delete Note
      // Delete the specified note id.
      deleteNote: async function(note) {
        var self = this;
        this.$buefy.dialog.confirm({
          title: 'Delete Note',
          message: `Are you sure you want to delete the note <b>${note.title}</b>?`,
          confirmText: 'Delete Note',
          focusOn: 'cancel',
          type: 'is-danger',
          onConfirm: async function() {
            await api.Notes.deleteNote(note.id);
            self.$root.$emit('notify', 'Note Deleted', `Successfully deleted note ${note.title}.`, 'mdi-check');
            self.note = {id:null, body:''};
            self.$refs.search.updateResults();
          },
        });
      },

      // Update Note
      // Load the specified note id.
      updateNote: async function(noteid) {
        var {data} = await api.Notes.getNote(noteid);
        this.note = data;
        this.editor.setContent(this.note.body);
        document.title = `PK - ${this.note.title}`;
      },
    },

  };
</script>

<style lang='scss'>
  #notes {
    #notewrap {
      width: 1170px;
      margin: 0px auto;
      position: relative;
      padding: 30px 30px 60px 30px;
    }
    #pagewrap { padding: 0px; }
    #page { float:left; }
    article {
      h1 input {
        background-color: transparent;
        border-width: 0px;
        border-radius: 0px;
        font-family: $fontfamily-title;
        font-size: 2rem;
        padding: 0px 3px;
        margin-left: -3px;
        width: 780px;
        color: $lightbg-text;
      }
      h1 .subtext,
      h1 .subtext input {
        font-size: 1rem;
        font-family: $fontfamily-article;
      }
      h1 .subtext input { width:250px; }
    }
    #rightmenu {
      float: left;
      font-size: .8rem;
      font-weight: 400;
      margin-left: 920px;
      position: fixed;
      width: 230px;
      .controls {
        font-size: 1rem;
        margin-top: 20px;
        color: $lightbg-link;
        .mdi { margin-right: 5px; }
      }
    }
  }
</style>
