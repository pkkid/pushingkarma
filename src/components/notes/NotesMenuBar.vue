<template>
  <div id='notesmenubar'>
    <transition name='fadein'>
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
      <button class='editbtn' v-else-if='userid !== null' @click='editing=true'>Edit</button>
    </transition>
    <!-- Success/Error message -->
    <transition name='fade'>
      <span class='message' v-if='message' :style='{color:message == "Error" ? "#fb4934":"#79740e"}'>
        <i v-if='message == "Error"' class='mdi mdi-alert-circle-outline'/>
        <i v-else class='mdi mdi-check-bold'/> {{message}}
      </span>
    </transition>
  </div>
</template>

<script>
  import Dropdown from '@/utils/components/Dropdown';
  import {buildquery} from '@/utils/utils';
  import {get, sync} from 'vuex-pathify';
  import {Editor, EditorMenuBar} from 'tiptap';
  import {Blockquote, BulletList, CodeBlockHighlight, HardBreak, Heading, Link,
    ListItem, OrderedList, Bold, Code, Italic, Strike, TodoItem, TodoList, Underline,
    History} from 'tiptap-extensions';
  import {FontSize} from '@/utils/tiptap-extensions';
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
    components: {EditorMenuBar, Dropdown},
    computed: {
      editing: sync('notes/editing'),
      editor: sync('notes/editor'),
      message: sync('notes/message'),
      note: sync('notes/note'),
      userid: get('global/user@id'),
    },
    data: () => ({
      linkUrl: null,        // Current URL text when editing links
      showLinkMenu: false,  // True when displaying link input
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
      // CurrentFormat: Return the currently selected text format
      currentFormat: function(isActive) {
        if (isActive.paragraph()) { return 'Paragraph'; }
        if (isActive.heading({level:1})) { return 'Heading 1'; }
        if (isActive.heading({level:2})) { return 'Heading 2'; }
        if (isActive.heading({level:3})) { return 'Heading 3'; }
        if (isActive.code_block()) { return 'Code Block'; }
        else { return 'Format'; }
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
  #notesmenubar {
    .message {
      right: calc(50% - 510px);
      position: fixed;
      text-align: right;
      top: 70px;
      z-index: 60;
      font-size: 15px;
      font-weight: 500;
      padding: 2px 0px;
      line-height: 23px;
    }

    .editbtn {
      margin-left: 780px;
      position: fixed;
      top: 70px;
      z-index: 50;
      background-color: darken($lightbg-color, 15%);
    }

    .menubar {
      background-color: $darkbg-color;
      border-radius: 8px;
      box-shadow: 0 2px 3px rgba(0, 0, 0, .3);
      color: $darkbg-text;
      padding: 5px 10px;
      position: fixed;
      top: 65px;
      width: 900px;
      margin-left: -51px;
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
        white-space: nowrap;
        padding: 2px 5px;
        font-size: 14px;
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
        button { width:100%; font-size:14px; margin:0px; }
      }
    }
  }

</style>
