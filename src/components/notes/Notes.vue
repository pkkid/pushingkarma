<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <div class='sidebar'>
      <Search ref='search'/>
    </div>
    <div class='content'>
      <div class='notebg'>
        <div class='notewrap'>
          <div class='note' :class='{editable:editing}'>
            <MenuBar ref='menubar' />
            <h1><input name='title' autocomplete='off' v-model='note.title' :readonly=!editing />
              <span>{{note.created | formatDate('MMM DD, YYYY')}}
              <input name='tags' placeholder='tags' autocomplete='off' v-model='note.tags' :readonly=!editing /></span>
            </h1>
            <editor-content id='editor' :editor='editor' />
          </div>
          <div class='toc'>
            <div v-for='item in toc' v-bind:key='item.text' :class='item.type'>
              {{item.text}}
            </div>
          </div>
          <div style='clear:both;'></div>
        </div>
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import Footer from '../Footer';
  import Navigation from '../Navigation';
  import MenuBar from './NotesMenuBar';
  import Search from './NotesSearch';
  import {sync} from 'vuex-pathify';
  // import {EditorContent} from 'tiptap';
  import {Editor, EditorContent} from 'tiptap';
  import {Blockquote, BulletList, CodeBlockHighlight, HardBreak, Heading, Link,
    ListItem, OrderedList, Bold, Code, Italic, Strike, TodoItem, TodoList, Underline,
    History} from 'tiptap-extensions';
  import {FontSize} from '@/utils/tiptap-extensions';
  import bash from 'highlight.js/lib/languages/bash';
  import css from 'highlight.js/lib/languages/css';
  import javascript from 'highlight.js/lib/languages/javascript';
  import python from 'highlight.js/lib/languages/python';

  export default {
    name: 'Notes',
    components: {Navigation, Footer, MenuBar, Search, EditorContent},
    data: () => ({
      toc: [],
    }),
    computed: {
      editing: sync('notes/editing'),
      editor: sync('notes/editor'),
      note: sync('notes/note'),
      title: sync('notes/note@title'),
      keymap: function() { return {
        'f1': (e) => this.$refs.search.focus(e),
        'e': (e) => this.$refs.menubar.startEditing(e),
        'ctrl+s': (e) => this.$refs.menubar.save(e),
        'esc': (e) => this.$refs.menubar.stopEditing(e),
      };},
    },

    watch: {
      // Watch Note
      // Update the TOC when the note changes
      note: function() { this.updateToc(); },
      title: function() { this.updateToc(); },
    },

    mounted: function() {
      // Tiptap Examples: https://github.com/scrumpy/tiptap
      // Tiptap Documentation: https://tiptap.scrumpy.io/docs
      this.$store.set('global/layout', 'topnav');
      this.editor = new Editor({
        editable: false,
        onUpdate: this.updateToc,
        extensions: [
          new Blockquote(),
          new Bold(),
          new BulletList(),
          new Code(),
          new CodeBlockHighlight({languages:{bash,css,javascript,python}}),
          new FontSize(),
          new HardBreak(),
          new Heading({levels:[1,2,3]}),
          new History(),
          new Italic(),
          new Link({openOnClick:false}),
          new ListItem(),
          new OrderedList(),
          new Strike(),
          new TodoItem({nested: true}),
          new TodoList(),
          new Underline(),
        ],
      });
    },

    methods: {
      // OnEditorUpdate
      // Called each time the editor is updated. We use this callback to
      // update the table of contents for the note.
      updateToc: function() {
        let toc = [{type:'h1', text:this.note.title}];
        for (let item of this.editor.getJSON().content) {
          if (item.type == 'heading') {
            toc.push({
              type: 'h'+ item.attrs.level,
              text: item.content[0].text,
            });
        }}
        this.toc = toc;
      },
    },

  };
</script>

<style lang='scss'>
  #notes .sidebar {
    float: left;
    width: 300px;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

  #notes .content {
    box-sizing: border-box;
    color: $lightbg-text;
    margin-left: 300px;
    margin-top: 60px;
    background-color: darken($lightbg-color, 10%);
    
    // General Scaffolding
    .notebg {
      padding: 50px 20px 60px 20px;
      box-shadow: inset 1px 0px 2px rgba(0,0,0,0.3);
    }
    .notewrap {
      width: 1150px;
      margin: 0px auto;
    }
  
    // Table of Contents
    .toc {
      border-left: 3px solid #076678;
      float: left;
      font-size: 0.8em;
      font-weight: 500;
      margin-left: 920px;
      margin-top: 3px;
      padding-left: 10px;
      position: fixed;
      width: 230px;
      line-height: 1.6em;
      .h1 { font-weight:bold; color:darken($lightbg-text, 30%); }
      .h2 { padding-left:0px; }
      .h3 { padding-left:20px; }
    }

    // General Note Display
    .note {
      float: left;
      width: 900px;
      margin: 0px auto;
      position: relative;
      min-height: calc(100vh - 70px);
      transition: padding 0.2s ease;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 10px 50px;
      background-color: $lightbg-color;
      //&.editable { padding-top: 60px; }
    }
    h1 {
      font-size: 1.9em;
      span { font-weight: 500; }
    }
    input {
      background-color: transparent;
      border-width: 0px;
      border-radius: 0px;
      &[name=title] {
        line-height: 1em;
        font-weight: 600;
        margin: 5px 0px 5px -2px;
        padding: 0px;
        text-transform: uppercase;
        white-space: normal;
      }
      &[name=tags] {
        line-height: 1em;
        font-weight: 500;
        width: 600px;
        padding: 0px 0px 3px 10px;
      }
    }
  }
</style>
