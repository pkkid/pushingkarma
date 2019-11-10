<template>
  <div id='notesmenubar'>
    <transition name='custom-classes-transition'
        enter-active-class='animated fadeIn'
        leave-active-class='animated fadeOut'>
      <editor-menu-bar :editor='editor' v-slot='{commands, getMarkAttrs, isActive}' v-if='editing'>
        <div class='menubar'>
          <!-- Format Menu Dropdown -->
          <Dropdown :width='"105px"'>
            <div slot='text'>{{currentFormat(isActive)}}</div>
            <div slot='menu'>
              <button :class='{"active":isActive.paragraph()}' @click='commands.paragraph'>Paragraph</button>
              <button :class='{"active":isActive.heading({level:1})}' @click='commands.heading({level:1})'>Heading 1</button>
              <button :class='{"active":isActive.heading({level:2})}' @click='commands.heading({level:2})'>Heading 2</button>
              <button :class='{"active":isActive.heading({level:3})}' @click='commands.heading({level:3})'>Heading 3</button>
              <button :class='{"active":isActive.code_block()}' @click='commands.code_block'>Code Block</button>
            </div>
          </Dropdown>
          <!-- Font Size -->
          <Dropdown :width='"55px"'>
            <div slot='text'>{{getMarkAttrs("fontSize").fontSize || "18px"}}</div>
            <div slot='menu'>
              <button :class='{"active":getMarkAttrs("fontSize").fontSize === "12px"}' @click='commands.fontSize({fontSize:"12px"})'>12px</button>
              <button :class='{"active":getMarkAttrs("fontSize").fontSize === "15px"}' @click='commands.fontSize({fontSize:"15px"})'>15px</button>
              <button :class='{"active":!("fontSize" in getMarkAttrs("fontSize"))}' @click='commands.fontSize({fontSize:null})'>18px</button>
              <button :class='{"active":getMarkAttrs("fontSize").fontSize === "22px"}' @click='commands.fontSize({fontSize:"22px"})'>22px</button>
              <button :class='{"active":getMarkAttrs("fontSize").fontSize === "26px"}' @click='commands.fontSize({fontSize:"26px"})'>26px</button>
            </div>
          </Dropdown>
          <!-- Regular Header Buttons -->
          <div class='sep'></div>
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
          <button @click.prevent='save' style='float:right;'><span>Save</span></button>
          <!-- Link Form -->
          <div class='link-form' v-if='showLinkMenu'>
            <input type='text' name='url' v-model='linkUrl' ref='linkInput' placeholder='https://' spellcheck='false' autocomplete='off'
              @keydown.enter.prevent='setLinkUrl(commands.link, linkUrl)'
              @keydown.esc.stop='hideLinkMenu'
              @click='$refs.linkInput.focus()'/>
            <button @click='setLinkUrl(commands.link, "")' style='margin-left:5px;'>Clear</button>
          </div>
        </div>
      </editor-menu-bar>
    </transition>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import Dropdown from '@/components/Dropdown';
  import {EditorMenuBar} from 'tiptap';

  // TipTap Extensions
  import {Blockquote, BulletList, CodeBlockHighlight, HardBreak, Heading,
    Link, ListItem, OrderedList, Bold, Code, Italic, Strike, TodoItem,
    TodoList, Underline, History} from 'tiptap-extensions';
  import {FontSize} from '@/utils/tiptap';
  import bash from 'highlight.js/lib/languages/bash';
  import css from 'highlight.js/lib/languages/css';
  import javascript from 'highlight.js/lib/languages/javascript';
  import python from 'highlight.js/lib/languages/python';

  export default {
    name: 'Notes',
    components: {EditorMenuBar, Dropdown},
    computed: {
      editing: pathify.sync('notes/editing'),
      editor: pathify.sync('notes/editor'),
      note: pathify.sync('notes/note'),
      userid: pathify.get('global/user@id'),
    },
    data: () => ({
      linkUrl: null,        // Current URL text when editing links
      showLinkMenu: false,  // True when displaying link input
    }),

    watch: {
      // Watch Editing
      // When edit mode changes, make sure TipTap is informed.
      editing: function() {
        let editable = this.editing && (this.userid !== null);
        this.editor.setOptions({editable});
      },

      // Watch UserID
      // If userid ever changes, make sure we stop editing.
      userid: function() {
        this.editing = false;
      }
    },

    methods: {
      // Extensions
      // Returns list of enabled tiptap extensions
      extensions: function() {
        return [
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
        ];
      },

      // CurrentFormat
      // Return the currently selected text format
      currentFormat: function(isActive) {
        if (isActive.paragraph()) { return 'Paragraph'; }
        if (isActive.heading({level:1})) { return 'Heading 1'; }
        if (isActive.heading({level:2})) { return 'Heading 2'; }
        if (isActive.heading({level:3})) { return 'Heading 3'; }
        if (isActive.code_block()) { return 'Code Block'; }
        else { return 'Format'; }
      },

      // Save
      // Save the current Title and Content to the server
      save: async function(event) {
        if (this.editing) {
          event.preventDefault();
          try {
            await api.Notes.saveNote(this.note.id, {
              title: this.note.title,
              tags: this.note.tags,
              body: this.editor.getHTML()
            });
            this.editing = false;
            this.$root.$emit('notify', 'Note saved!', 'mdi-check');
          } catch(err) {
            this.$root.$emit('notify', 'Error saving note.', 'mdi-alert-circle-outline');
          }
        }
      },

      // StartEditing
      // Enable editing mode for this note
      startEditing: function(event) {
        let loggedin = this.userid !== null;
        let isinput = event && event.srcElement.tagName == 'INPUT';
        if (loggedin && !this.editing && !isinput) {
          if (event) event.preventDefault();
          this.editing = true;
        }
      },

      // StopEditing
      // Disable editing mode for this note
      stopEditing: function(event) {
        if (this.editing) {
          if (event) event.preventDefault();
          this.editing = false;
        }
      },

      // ToggleLinkMenu
      // Show or hide the link menu input
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

      // HideLinkMenu
      // Hide the link menu without changing anything
      hideLinkMenu: function() {
        this.linkUrl = null;
        this.showLinkMenu = false;
      },

      // SetLinkURL
      // Set the link URL then hide the link menu
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
  #notesmenubar {
    .menubar {
      animation-duration: .3s;
      background-color: $darkbg-color;
      border-radius: 8px;
      box-shadow: 0 2px 3px rgba(0, 0, 0, .3);
      color: $darkbg-text;
      padding: 5px 10px;
      position: fixed;
      top: 70px;
      width: 900px;
      margin-left: -51px;
      z-index: 50;
      line-height: 1.6em;
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
        line-height: 1.6em;
        i.mdi { font-size:2.0rem; position:relative; top:1px; }
        &:hover { background-color: lighten($darkbg-color, 8%); }
        &.active { background-color: lighten($darkbg-color, 16%); }
        &.icon { padding: 2px 5px; }
      }
      input {
        background-color: rgba(255,255,255,0.1);
        border-radius: 4px;
        border-width: 0px;
        color: $darkbg-input;
        font-size: 1.3rem;
        font-weight: 500;
        line-height: 1.6em;
        margin-top: 5px;
        padding: 2px 8px;
        width: 700px;
      }
      .dropdown {
        position: relative;
        white-space: nowrap;
        padding: 2px 5px;
        font-size: 1.4rem;
        top: -2px;
        i.mdi { position:absolute; right:5px; top:2px; }
      }
      .dropdown-menu {
        background-color: $darkbg-color;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        left: -10px;
        line-height: 30px;
        padding: 5px 10px;
        position: absolute;
        top: 27px;
        white-space: normal;
        z-index: 51;
        button { width:100%; margin:0px; }
      }
    }
  }

</style>
