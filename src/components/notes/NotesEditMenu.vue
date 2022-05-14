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
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleTaskList().run()" :class="{'active':editor.isActive('taskList')}"><b-icon size='is-small' icon='format-list-checkbox'/></b-button>
        <div class='sep'/>
        <!-- Block Quote, Code, Link -->
        <b-button type='is-text is-small' @click="showImageMenu(true)" :class="{'active':editor.isActive('image')}"><b-icon size='is-small' icon='image'/></b-button>
        <b-button type='is-text is-small' @click="showLinkMenu(true)" :class="{'active':editor.isActive('link')}"><b-icon size='is-small' icon='link'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleBlockquote().run()" :class="{'active':editor.isActive('blockquote')}"><b-icon size='is-small' icon='format-quote-close'/></b-button>
        <b-button type='is-text is-small' @click="editor.chain().focus().toggleCode().run()" :class="{'active':editor.isActive('code')}"><b-icon size='is-small' icon='code-tags'/></b-button>
        <!-- Save -->
        <b-button type='is-text is-small' @click.prevent='save' style='float:right;'><span>Save Note</span></b-button>
        <!-- Link Menu (hidden by default) -->
        <div v-if='imageMenuVisible' class='expandform'>
          <label>Image URL</label>
          <input type='text' name='url' class='input' v-model='imageUrl' ref='imageInput' placeholder='https://' spellcheck='false' autocomplete='off'
            @keydown.enter.prevent="hideImageMenu(true)"
            @keydown.esc.stop='hideImageMenu()'/>
        </div>
        <!-- Link Menu (hidden by default) -->
        <div v-if='linkMenuVisible' class='expandform'>
          <label>Link URL</label>
          <input type='text' name='url' class='input' v-model='linkUrl' ref='linkInput' placeholder='https://' spellcheck='false' autocomplete='off'
            @keydown.enter.prevent="hideLinkMenu(true)"
            @keydown.esc.stop='hideLinkMenu(false)'/>
          <b-button type='is-text is-small' @click='editor.commands.unsetLink(); linkUrl=""'>Unlink</b-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';

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
      imageUrl: null,           // Current URL text when editing images
      imageMenuVisible: false,  // True when displaying image input
      linkUrl: null,            // Current URL text when editing links
      linkMenuVisible: false,   // True when displaying link input
    }),

    // BeforeDestory: Cleanup the editor
    beforeDestroy: function() {
      this.editor.destroy();
    },

    watch: {
      // Watch Editing
      // When edit mode changes, make sure TipTap is informed.
      editing: function() {
        let editable = this.editing && (this.userid !== null);
        this.linkMenuVisible = false;
        this.editor.setOptions({editable});
      },

      // Watch UserID
      // If userid ever changes, make sure we stop editing.
      userid: function() {
        this.editing = false;
      },

      // Watch linkUrl
      // Update the selected text link url when the model changes.
      // linkUrl: function() {
      //   if (this.linkUrl) { this.editor.commands.setLink({href:this.linkUrl}); }
      // }
    },

    methods: {
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
            this.$root.$emit('notify', 'Note Saved',
              'This note was successfully saved to the server.', 'mdi-check');
          } catch(err) {
            this.$root.$emit('notify', 'Error Saving Note.', `There was an error
              attempting to save this note to the server. Please backup your work
              and try again.`, 'mdi-alert-circle-outline');
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

      // onSelectionUpdate
      // Update the link menu status
      onSelectionUpdate: function() {
        this.imageUrl = this.editor.getAttributes('image').src;
        this.imageUrl ? this.showImageMenu() : this.hideImageMenu();
        this.linkUrl = this.editor.getAttributes('link').href;
        this.linkUrl ? this.showLinkMenu() : this.hideLinkMenu();
      },


      // ----------------------
      // ShowImageMenu
      // Hide the image menu without changing anything 
      showImageMenu: function(focus=false) {
        this.imageUrl = this.imageUrl || 'http://';
        this.imageMenuVisible = true;
        if (focus) {
          this.$nextTick(function() {
            self.$refs.imageInput.focus();
          });
        }
      },

      // HideImageMenu
      // Save the URL and Hide the image menu
      hideImageMenu: function(save=false) {
        if (save && this.imageUrl) {
          this.editor.chain().focus().setImage({src:this.imageUrl}).run();
        }
        this.imageMenuVisible = false;
        this.imageUrl = '';
      },

      // ----------------------
      // ShowLinkMenu
      // Hide the link menu without changing anything 
      showLinkMenu: function(focus=false) {
        var self = this;
        this.linkUrl = this.linkUrl || 'http://';
        this.linkMenuVisible = true;
        if (this.linkUrl == 'http://') {
          this.editor.commands.setLink({href:this.linkUrl});
        }
        if (focus) {
          this.$nextTick(function() {
            self.$refs.linkInput.focus();
          });
        }
      },

      // HideLinkMenu
      // Save the URL and Hide the link menu
      hideLinkMenu: function(save=false) {
        if (!this.linkUrl || this.linkUrl.length < 12) {
          this.editor.chain().focus().extendMarkRange('link')
            .unsetLink().run();
        }
        if (save && this.linkUrl && this.linkUrl.length >= 12) {
          this.editor.chain().focus().extendMarkRange('link')
            .setLink({href:this.linkUrl}).run();
        }
        this.linkMenuVisible = false;
      },

    },
  };
</script>

<style lang='scss'>
  .editing #editor a {
    cursor: text;
  }
  #notesmenubar .menubar {
    animation-duration: .3s;
    background-color: $darkbg-color;
    border-radius: 4px;
    box-shadow: 0 2px 3px rgba(0, 0, 0, .3);
    color: $darkbg-text;
    line-height: 2.1em;
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
      font-size: 0.8rem;
      label {
        float: left;
        margin-right: 10px;
        opacity: 0.7;
        text-align: right;
        width: 70px;
        height: 28px;
        line-height: 28px;
        padding-top: 1px;
      }
      .input {
        background-color: #444;
        border-width: 0px;
        color: $darkbg-input;
        float: left;
        font-size: 0.8rem;
        font-weight: 500;
        height: 28px;
        line-height: 25px;
        margin-bottom: 5px;
        padding-top: 6px;
        width: calc(100% - 200px);
      }
      .button {
        margin-left: 5px;
        height: 28px;
        font-size: 0.8rem;
      }
    }
    
  }
</style>
