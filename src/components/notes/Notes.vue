<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <div id='sidebar'>
      <Search ref='search'/>
    </div>
    <div class='content'>
      <div class='notebg' :class='{editable:editing}'>
        <div class='notewrap'>
          <div class='note'>
            <MenuBar ref='menubar' />
            <h1><input name='title' autocomplete='off' placeholder='Enter a Title' v-model='note.title' :readonly=!editing />
              <div class='subtext'>
                {{note.created | formatDate('MMM DD, YYYY')}}
                <input name='tags' placeholder='tags' autocomplete='off' v-model='note.tags' :readonly=!editing />
              </div>
            </h1>
            <editor-content id='editor' :editor='editor' />
          </div>
          <div id='rightpanel'>
            <div class='toc'>
              <div v-for='item in toc' v-bind:key='item.text' :class='item.type'>
                <router-link :to='{hash:item.slug, query:$route.query}'>{{item.text}}</router-link>
              </div>
            </div>
            <div class='controls' if='userid !== null'>
              <!-- Edit buttons -->
              <div v-if='editing'><i class='mdi mdi-cancel'/> <a @click='editing=false'>Cancel Changes</a></div>
              <div v-else><i class='mdi mdi-pencil-outline'/> <a @click='editing=true'>Edit Note</a></div>
              <!-- Success/Error message -->
              <transition name='fade'>
                <span class='message' v-if='message' :style='{color:message == "Error" ? "#9d0006":"#79740e"}'>
                  <i v-if='message == "Error"' class='mdi mdi-alert-circle-outline'/>
                  <i v-else class='mdi mdi-check-bold'/>{{message}}
                </span>
              </transition>
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
  import {get, sync} from 'vuex-pathify';
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
      message: sync('notes/message'),
      note: sync('notes/note'),
      title: sync('notes/note@title'),
      userid: get('global/user@id'),
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

      // Watch Message
      // A simple fading Success/Error message on save
      message: function() {
        let self = this;
        if (this.message) { setTimeout(function() { self.message = null; }, 3000); }
      },
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
      // Update TOC
      // Called each time the editor is updated. We use this callback to
      // update the table of contents for the note.
      updateToc: function() {
        let toc = [{text:this.note.title, slug:'#title', type:'h1'}];
        for (let item of this.editor.getJSON().content) {
          if (item.type == 'heading') {
            var text = item.content[0].text;
            toc.push({
              text: text,
              slug: '#'+ text.toLowerCase().replace(/\s/g, '_'),
              type: 'h'+ item.attrs.level,
            });
        }}
        this.toc = toc;
      },
    },

  };
</script>

<style lang='scss'>
  #sidebar {
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
      padding: 30px 20px 60px 20px;
      box-shadow: inset 1px 0px 2px rgba(0,0,0,0.3);
      transition: padding 0.2s ease;
      &.editable { padding-top: 60px; }
    }
    .notewrap {
      width: 1150px;
      margin: 0px auto;
    }
  
    // Table of Contents
    #rightpanel {
      float: left;
      font-size: 0.8em;
      font-weight: 500;
      margin-left: 920px;
      margin-top: 3px;
      position: fixed;
      width: 230px;
      line-height: 1.7em;
      .toc {
        border-left: 3px solid #076678;
        padding-left: 10px;
        .h1 { font-weight:bold; color:darken($lightbg-text, 30%); }
        .h2 { padding-left:0px; }
        .h3 { padding-left:20px; }
        a {
          color: $lightbg-text;
          &:hover { color:$lightbg-link; text-decoration:none; }
        }
      }
      .controls {
        margin-top: 20px;
        color: $lightbg-link;
        .mdi { margin-right: 5px; }
      }
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
      padding: 25px 50px;
      background-color: $lightbg-color;
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
