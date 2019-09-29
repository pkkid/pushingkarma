<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <div class='sidebar'><Search ref='search'/></div>
    <div class='content'>
      <div class='note' :class='{editable:editing}'>
        <!-- Menubar -->
        <transition name='fade'>
          <editor-menu-bar :editor='editor' v-slot='{commands, getMarkAttrs, isActive}' v-if='editing'>
            <div class='menubar'>
              <!-- Format Menu Dropdown -->
              <button class='dropdown' v-on:click.prevent="showFormatMenu=!showFormatMenu">
                <span v-if='isActive.paragraph()'>Paragraph</span>
                <span v-else-if='isActive.heading({level:1})'>Heading 1</span>
                <span v-else-if='isActive.heading({level:2})'>Heading 2</span>
                <span v-else-if='isActive.heading({level:3})'>Heading 3</span>
                <span v-else-if='isActive.code_block()'>Code Block</span>
                <span v-else>Format</span> <i class='mdi mdi-menu-down'/>
              </button>
              <div v-if='showFormatMenu' class='dropdown-menu'>
                <button :class='{"active":isActive.paragraph()}' @click='commands.paragraph'>Paragraph</button>
                <button :class='{"active":isActive.heading({level:1})}' @click='commands.heading({level:1})'>Heading 1</button>
                <button :class='{"active":isActive.heading({level:2})}' @click='commands.heading({level:2})'>Heading 2</button>
                <button :class='{"active":isActive.heading({level:3})}' @click='commands.heading({level:3})'>Heading 3</button>
                <button :class='{"active":isActive.code_block()}' @click='commands.code_block'>Code Block</button>
              </div>
              <div class='sep'></div>
              <!-- Regular Header Buttons -->
              <button class='icon' :class='{"active":isActive.bold()}' @click='commands.bold'><i class='mdi mdi-format-bold'/></button>
              <button class='icon' :class='{"active":isActive.italic()}' @click='commands.italic'><i class='mdi mdi-format-italic'/></button>
              <button class='icon' :class='{"active":isActive.underline()}' @click='commands.underline'><i class='mdi mdi-format-underline'/></button>
              <div class='sep'></div>
              <button class='icon' :class='{"active":isActive.bullet_list()}' @click='commands.bullet_list'><i class='mdi mdi-format-list-bulleted'/></button>
              <button class='icon' :class='{"active":isActive.ordered_list()}' @click='commands.ordered_list'><i class='mdi mdi-format-list-numbered'/></button>
              <button class='icon' :class='{"active":isActive.todo_list()}' @click="commands.todo_list"><i class='mdi mdi-format-list-checkbox'/></button>
              <div class='sep'></div>
              <button class='icon' :class='{"active":isActive.link()}' @click='toggleLinkMenu(getMarkAttrs("link"))'><i class='mdi mdi-link'/></button>
              <button class='icon' :class='{"active":isActive.blockquote()}' @click='commands.blockquote'><i class='mdi mdi-format-quote-close'/></button>
              <button class='icon' :class='{"active":isActive.code()}' @click='commands.code'><i class='mdi mdi-code-tags'/></button>
              <button @click='save' style='float:right;'><span>Save</span></button>
              <!-- Link Form -->
              <div class='link-form' v-if='showLinkMenu'>
                <input type='text' name='url' v-model='linkUrl' ref='linkInput' placeholder='https://' spellcheck='false' autocomplete='off'
                  @keydown.enter.prevent='setLinkUrl(commands.link, linkUrl)'
                  @keydown.esc.stop='hideLinkMenu'
                  @click='$refs.linkInput.focus()'/>
                <button @click='setLinkUrl(commands.link, "")' style='margin-left:5px; font-size:14px;'>Clear</button>
              </div>
            </div>
          </editor-menu-bar>
          <button class='edit' v-else-if='userid !== null' @click='editing=true'>Edit</button>
        </transition>
        <!-- Success/Error message -->
        <transition name='fade'>
          <span class='message' v-if='message' :style='{color:message == "Error" ? "#fb4934":"#79740e"}'>
            <i v-if='message == "Error"' class='mdi mdi-alert-circle-outline'/>
            <i v-else class='mdi mdi-check-bold'/> {{message}}
          </span>
        </transition>
        <!-- Content -->
        <h1>
          <input name='title' autocomplete='off' v-model='note.title' :readonly=!editing />
          <span>{{note.created | formatDate('MMM DD, YYYY')}}
            <input name='tags' placeholder='tags' autocomplete='off' v-model='note.tags' :readonly=!editing /></span>
        </h1>
        <editor-content :editor='editor' />
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import Footer from '../Footer';
  import Navigation from '../Navigation';
  import Search from './NotesSearch';
  import {Editor, EditorContent, EditorMenuBar} from 'tiptap';
  import {Blockquote, BulletList, CodeBlockHighlight, HardBreak, Heading,
    ListItem, OrderedList, Bold, Code, Italic, Link, Strike, TodoItem, TodoList, Underline,
    History} from 'tiptap-extensions';
  import {buildquery} from '@/utils/utils';
  import {get, sync} from 'vuex-pathify';

  import bash from 'highlight.js/lib/languages/bash';
  import css from 'highlight.js/lib/languages/css';
  import javascript from 'highlight.js/lib/languages/javascript';
  import python from 'highlight.js/lib/languages/python';

  var QUERY_SAVENOTE = `mutation saveNote {
    saveNote(id:{id}, title:{title}, tags:{tags}, body:{body}) {
      note { id slug title tags body created }
      success
    }}`;

  export default {
    name: 'Notes',
    components: {Navigation, Footer, Search, EditorContent, EditorMenuBar},
    computed: {
      editor: sync('notes/editor'),
      note: sync('notes/note'),
      userid: get('global/user@id'),
      keymap: function() { return {
        'f1': this.hotkeyFocusSearch,
        'e': this.hotkeyEditNote,
        'ctrl+s': this.hotkeySaveNote,
        'esc': this.hotkeyStopEditing,
      };},
    },
    data: () => ({
      editing: false,
      message: null,
      linkUrl: null,
      showFormatMenu: false,
      showLinkMenu: false,
    }),
    watch: {
      editing: function() {
        let editable = this.editing && (this.userid !== null);
        this.editor.setOptions({editable});
      },
      message: function() {
        let self = this;
        if (this.message) {
          setTimeout(function() { self.message = null; }, 3000);
        }
      },
      userid: function() {
        this.editing = false;
      }
    },

    mounted: function() {
      // Tiptap Examples: https://github.com/scrumpy/tiptap
      // Tiptap Documentation: https://tiptap.scrumpy.io/docs
      this.$store.set('global/layout', 'topnav');
      this.editor = new Editor({
        editable: false,
        extensions: [
          new Blockquote(),
          new Bold(),
          new BulletList(),
          new Code(),
          new CodeBlockHighlight({languages: {bash, css, javascript, python}}),
          new HardBreak(),
          new Heading({levels: [1, 2, 3]}),
          new History(),
          new Italic(),
          new Link(),
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

      // HotkeyEditNote: Edit the current note
      hotkeyEditNote: function(event) {
        if (!this.editing && (this.userid !== null) && (event.srcElement.tagName != 'INPUT')) {
          event.preventDefault();
          this.editing = true;
        }
      },

      // HotkeyFocusSearch: Focus and select all text in the search input
      hotkeyFocusSearch: function(event) {
        event.preventDefault();
        this.$refs.search.$refs.search.select();
      },

      // HotkeySaveNote: Save the current note.
      hotkeySaveNote: function(event) {
        event.preventDefault();
        if (this.editing) { this.save(); }
      },

      // HotkeyStopEditing: Stop editing the current note (do not save)
      hotkeyStopEditing: function(event) {
        if (this.editing) {
          event.preventDefault();
          this.editing = false;
        }
      },

      // Save: Save the current Title and Content to the server
      save: function() {
        let self = this;
        let data = {id:self.note.id, title:self.note.title,
          tags:self.note.tags, body:self.editor.getHTML()};
        let request = buildquery(QUERY_SAVENOTE, data);
        request.xhr.then(function() {
          self.editing = false;
          self.message = 'Success';
        });
        request.xhr.catch(function() {
          self.message = 'Error';
        });
      },

      // ToggleLinkMenu: Show or hide the link menu input
      // see: https://tiptap.scrumpy.io/links
      toggleLinkMenu: function(attrs) {
        if (this.showLinkMenu) {
          this.hideLinkMenu();
        } else {
          this.linkUrl = attrs.href;
          this.showLinkMenu = true;
          this.$nextTick(function() {
            this.$refs.linkInput.focus();
          });
        }
      },

      // HideLinkMenu: Hide the link menu without changing anything
      hideLinkMenu: function() {
        this.linkUrl = null;
        this.showLinkMenu = false;
      },

      // SetLinkURL: Set the link URL then hide the link menu
      setLinkUrl: function(command, url) {
        command({href: url});
        this.hideLinkMenu();
      },
    },

    // BeforeDestory: Cleanup the editor
    beforeDestroy: function() {
      this.editor.destroy();
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
    background-color: $lightbg-color;
    box-sizing: border-box;
    color: $lightbg-text;
    margin-left: 300px;
    margin-top: 60px;
    
    // General Note Display
    .note {
      width: 800px;
      margin: 20px auto;
      padding-top: 10px;
      position: relative;
      min-height: calc(100vh - 70px);
      transition: padding 0.2s ease;
      &.editable { padding-top: 60px; }
    }
    .edit {
      margin-left: 730px;
      position: fixed;
      top: 70px;
      z-index: 50;
    }
    .message {
      right: calc(50% - 460px);
      position: fixed;
      text-align: right;
      top: 70px;
      z-index: 60;
      font-size: 15px;
      font-weight: 500;
      padding: 2px 0px;
      line-height: 23px;
    }
    input {
      background-color: transparent;
      border-width: 0px;
      border-radius: 0px;
      &[name=title] {
        font-size: 40px;
        font-weight: 600;
        margin: 5px 0px 5px -2px;
        padding: 0px;
        text-transform: uppercase;
        white-space: normal;
        line-height: 40px;
      }
      &[name=tags] {
        font-size: 16px;
        font-weight: 400;
        width: 600px;
        padding: 0px 0px 3px 10px;
      }
    }

    // Menubar and Buttons
    .menubar {
      background-color: $darkbg-color;
      border-radius: 8px;
      box-shadow: 0 2px 3px rgba(0, 0, 0, .3);
      color: $darkbg-text;
      padding: 5px 10px;
      position: fixed;
      top: 65px;
      width: 800px;
      z-index: 50;
      line-height: 23px;
      .sep {
        margin: 0px 10px 0px 5px;
        background-color: red;
        display: inline;
        border-left: 1px solid #665c54;
      }
      button {
        background-color: transparent;
        background-image: none;
        color: $darkbg-text;
        margin-right: 5px;
        span { font-size: 16px; }
        i.mdi { font-size:20px; position:relative; top:1px; }
        &:hover { background-color: lighten($darkbg-color, 8%); }
        &.active { background-color: lighten($darkbg-color, 16%); }
        &.icon { padding: 2px 5px; }
      }
      input {
        background-color: rgba(255,255,255,0.1);
        border-radius: 4px;
        border-width: 0px;
        color: $darkbg-input;
        font-size: 14px;
        font-weight: 500;
        line-height: 23px;
        margin-top: 5px;
        padding: 2px 8px;
        width: 700px;
      }
      .dropdown {
        position: relative;
        width: 140px;
      }
      .dropdown-menu {
        background-color: $darkbg-color;
        border-radius: 8px;
        left: 0px;
        line-height: 30px;
        padding: 5px 10px;
        position: absolute;
        top: 42px;
        width: 150px;
        z-index: 51;
        button {
          width: 130px;
          text-align: left;
          font-size: 16px;
        }
      }
    }
  }
</style>
