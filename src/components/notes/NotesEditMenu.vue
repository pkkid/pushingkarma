<template>
  <div id='notesmenubar'>
    <transition name='custom-classes-transition' enter-active-class='animated fadeIn' leave-active-class='animated fadeOut'>
      <div v-if='editing' class='menubar'>
        
        <!-- Paragraph Style -->
        <b-dropdown>
          <button class='button is-text is-small texttype' slot='trigger' slot-scope='{active}'>
            <span>{{currentFormat(editor)}}</span>
            <b-icon :icon="active ? 'menu-up':'menu-down'"></b-icon>
          </button>
          <b-dropdown-item @click='editor.chain().focus().setParagraph().run()' :class='{"active":editor.isActive("paragraph")}'>Paragraph</b-dropdown-item>
          <b-dropdown-item @click='editor.chain().focus().toggleHeading({level:1}).run()' :class='{"active":editor.isActive("heading", {level:1})}'>Heading 1</b-dropdown-item>
          <b-dropdown-item @click='editor.chain().focus().toggleHeading({level:2}).run()' :class='{"active":editor.isActive("heading", {level:2})}'>Heading 2</b-dropdown-item>
          <b-dropdown-item @click='editor.chain().focus().toggleHeading({level:3}).run()' :class='{"active":editor.isActive("heading", {level:3})}'>Heading 3</b-dropdown-item>
          <b-dropdown-item @click='editor.chain().focus().toggleCodeBlock().run()' :class='{"active":editor.isActive("codeBlock")}'>Code Block</b-dropdown-item>
        </b-dropdown>
        <div class='sep'/>
        <!-- Bold, Italic, Strike -->
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleBold().run()" :class="{'active':editor.isActive('bold')}"><b-icon size='is-small' icon='format-bold'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleItalic().run()" :class="{'active':editor.isActive('italic')}"><b-icon size='is-small' icon='format-italic'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleStrike().run()" :class="{'active':editor.isActive('strike')}"><b-icon size='is-small' icon='format-strikethrough'/></b-button>
        <div class='sep'/>
        <!-- Lists -->
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleBulletList().run()" :class="{'active':editor.isActive('bulletList')}"><b-icon size='is-small' icon='format-list-bulleted'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleOrderedList().run()" :class="{'active':editor.isActive('orderedList')}"><b-icon size='is-small' icon='format-list-numbered'/></b-button>
        <div class='sep'/>
        <!-- Block Quote, Code, Link -->
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleBlockquote().run()" :class="{'active':editor.isActive('blockquote')}"><b-icon size='is-small' icon='format-quote-close'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleCode().run()" :class="{'active':editor.isActive('code')}"><b-icon size='is-small' icon='code-tags'/></b-button>
        <b-button type='is-text is-small' @click="toggleLinkMenu()" :class="{'active':editor.isActive('link')}"><b-icon size='is-small' icon='link'/></b-button>
        <!-- Save -->
        <b-button type='is-text is-small' @click.prevent='save' style='float:right;'><span>Save</span></b-button>
        <!-- Link Menu (hidden by default) -->
        <div v-if='showLinkMenu' class='expandform'>
          <input type='text' name='url' class='input' v-model='linkUrl' ref='linkInput' placeholder='https://' spellcheck='false' autocomplete='off'
            @keydown.enter.prevent="editor.commands.setLink({href:linkUrl})"
            @keydown.esc.stop='hideLinkMenu'
            @click='$refs.linkInput.focus()'/>
          <b-button type='is-text is-small' @click='editor.commands.unsetLink(); linkUrl=""'>Remove Link</b-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import StarterKit from '@tiptap/starter-kit';
  import Code from '@tiptap/extension-code';
  import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
  import Link from '@tiptap/extension-link';
  import Strike from '@tiptap/extension-strike';
  import TaskItem from '@tiptap/extension-task-item';
  import TaskList from '@tiptap/extension-task-item';

  import bash from 'highlight.js/lib/languages/bash';
  import css from 'highlight.js/lib/languages/css';
  import javascript from 'highlight.js/lib/languages/javascript';
  import python from 'highlight.js/lib/languages/python';
  import sql from 'highlight.js/lib/languages/sql';
  import xml from 'highlight.js/lib/languages/xml';
  var LANGUAGES = {bash,css,javascript,python,sql,xml};

  export default {
    name: 'NotesEditMenu',
    //components: {EditorMenuBar},
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
        this.showLinkMenu = false;
        this.editor.setOptions({editable});
      },

      // Watch UserID
      // If userid ever changes, make sure we stop editing.
      userid: function() {
        this.editing = false;
      }
    },

    methods: {
      bold: function() {
        this.editor.chain().focus().toggleBold().run();
      },

      // Extensions
      // Returns list of enabled tiptap extensions
      extensions: function() {
        return [
          StarterKit,
          Code,
          CodeBlockLowlight,
          Link.configure({openOnClick: false}),
          Strike,
          TaskItem,
          TaskList
        ];
      },

      // CurrentFormat
      // Return the currently selected text format
      currentFormat: function(editor) {
        if (editor.isActive('paragraph')) { return 'Paragraph'; }
        if (editor.isActive('heading', {level:1})) { return 'Heading 1'; }
        if (editor.isActive('heading', {level:2})) { return 'Heading 2'; }
        if (editor.isActive('heading', {level:3})) { return 'Heading 3'; }
        if (editor.isActive('codeBlock')) { return 'Code Block'; }
        return 'Format';
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
            this.$root.$emit('notify', 'Note Saved', 'This note was successfully saved to the server.', 'mdi-check');
          } catch(err) {
            this.$root.$emit('notify', 'Error Saving Note.', `There was an error attempting to save this note to
              the server. Please backup your work and try again.`, 'mdi-alert-circle-outline');
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
      toggleLinkMenu: function() {
        var self = this;
        if (this.showLinkMenu) {
          return this.hideLinkMenu();
        }
        // TODO: Update the linkURL every time the cursor changes
        this.linkUrl = this.editor.getAttributes('link').href;
        this.showLinkMenu = true;
        this.$nextTick(function() {
          self.$refs.linkInput.focus();
        });
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
  #notesmenubar .menubar {
    animation-duration: .3s;
    background-color: $darkbg-color;
    border-radius: 4px;
    box-shadow: 0 2px 3px rgba(0, 0, 0, .3);
    color: $darkbg-text;
    line-height: 2.3em;
    margin-left: -40px;
    padding: 5px 10px 2px 10px;
    position: fixed;
    top: 70px;
    width: 920px;
    z-index: 50;
    :focus { box-shadow: none; }
    .sep {
      margin: 0px 10px 0px 5px;
      display: inline;
      border-left: 1px dotted #665c54;
    }
    .button {
      background-color: transparent;
      color: $darkbg-text;
      text-decoration: none;
      margin-right: 5px;
      padding: 15px 10px 13px 10px;
      height: 32px;
      &:hover { background-color: lighten($darkbg-color, 8%); }
      &.active { background-color: lighten($darkbg-color, 16%); }
      &.is-text {
        font-size: 0.9em;
        height: 25px;
      }
      &.texttype { width: 120px; }
      .mdi { font-size: 20px; }
    }
    .expandform {
      margin-top: 5px;
      .input {
        background-color: #444;
        border-width: 0px;
        color: $darkbg-input;
        float: left;
        font-size: 0.9em;
        font-weight: 500;
        line-height: 25px;
        margin-bottom: 5px;
        height: 32px;
        padding-top: 6px;
        width: calc(100% - 200px);
      }
      .button {
        margin-left: 5px;
      }
    }
    
  }
</style>
