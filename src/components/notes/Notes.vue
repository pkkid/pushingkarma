<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <SidePanel>
      <template v-slot:sidepanel>
        <Search ref='search' @newSelection='updateNote'/>
      </template>
      <template v-slot:contentarea>
        <div id='notewrap' :class='{editing}'>
          <!-- Edit Menu & Note -->
          <PageWrap>
            <NotesEditMenu ref='editmenu'/>
            <h1><input name='title' autocomplete='off' placeholder='Enter a Title' v-model='note.title' :readonly=!editing />
              <div class='subtext'>
                {{note.modified | formatDate('MMM DD, YYYY')}} &nbsp;•&nbsp;
                <input name='tags' placeholder='tags' autocomplete='off' v-model='note.tags' :readonly=!editing />
              </div>
            </h1>
            <editor-content id='editor' :editor='editor' />
          </PageWrap>
          <!-- Table of Contents & Edit Controls -->
          <div id='rightmenu'>
            <NotesToc :title='title' :content='content'/>
            <NotesMeta :note='note' :tagstr='note.tags' :search='$refs.search'/>
            <div v-if='userid'>
              <h2 style='margin-top:40px;'>Editing Options</h2>
              <div class='submenu'>
                <div v-if='editing'><a @click='editing=false'>Cancel Changes</a></div>
                <div v-else>
                  <div><a @click='editing=true'>Edit Note</a></div>
                  <div><a @click='createNote(note)'>Create Note</a></div>
                  <div><a @click='deleteNote(note)'>Delete Note</a></div>
                </div>
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
  import NotesMeta from './NotesMeta';
  import Search from './NotesSearch';
  // TipTap and Extensions
  import {Editor, EditorContent} from '@tiptap/vue-2';
  import StarterKit from '@tiptap/starter-kit';
  import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
  import Link from '@tiptap/extension-link';
  import TaskItem from '@tiptap/extension-task-item';
  import TaskList from '@tiptap/extension-task-list';
  import lowlight from 'lowlight';

  export default {
    name: 'Notes',
    components: {Navigation, SidePanel, PageWrap, NotesEditMenu, NotesToc, NotesMeta, Search, EditorContent},
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
        onSelectionUpdate: this.onSelectionUpdate,
        extensions: [
          StarterKit,
          CodeBlockLowlight.configure({lowlight, languageClassPrefix:'_'}),
          Link.configure({openOnClick:false}),
          TaskItem.configure(),
          TaskList,
        ],
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

      // On Selection Update
      // Keeps the Link href form up to date.
      onSelectionUpdate: function() {
        if (this.editing) {
          this.$refs.editmenu.linkUrl = this.editor.getAttributes('link').href;
        }
      },

      // Update Note
      // Load the specified note id.
      updateNote: async function(noteid) {
        var {data} = await api.Notes.getNote(noteid);
        this.note = data;
        this.editor.commands.setContent(this.note.body);
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
      #pagewrap { float:left; margin-top:0px; transition: margin 0.2s ease; }
      &.editing #pagewrap { margin-top:35px; background-color: $lightbg-blue1; }
    }

    article {
      h1 input {
        background-color: darken($lightbg-bg1, 5%);
        border-width: 0px;
        border-radius: 3px;
        font-family: $fontfamily-title;
        font-size: 2rem;
        padding: 0px 5px;
        margin-left: -5px;
        width: 840px;
        color: $lightbg-text;
        transition: background-color 0.2s ease;
        &:read-only {
          background-color: transparent;
        }
      }
      h1 .subtext,
      h1 .subtext input {
        font-size: 1rem;
        font-family: $fontfamily-article;
      }
      h1 .subtext input { width:700px; }
    }
    #rightmenu {
      float: left;
      font-size: 1rem;
      font-weight: 400;
      margin-left: 920px;
      position: fixed;
      width: 250px;
      h2 {
        color: $lightbg-fg0;
        font-size: 1.1em;
        margin-bottom: 10px;
        margin-top: 40px;
      }
      .submenu {
        border-left: 3px solid $lightbg-blue1;
        font-size: 0.9em;
        padding-left: 10px;
        a {
          color: $lightbg-text;
          margin-right: 3px;
          &:hover { color:$lightbg-link; text-decoration:none; }
        }
      }
    }
    // Display the language for code samples
    pre { position: relative; }
    code[class*='_']::before {
      color: #777;
      content: attr(class);
      font-size: 0.7rem;
      position: absolute;
      right: 10px;
      top: 10px;
    }
  }
</style>
