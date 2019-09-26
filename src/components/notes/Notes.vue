<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'><Search/></div>
    <div class='content'>
      <div class='note'>
        <!-- Menubar -->
        <editor-menu-bar :editor='editor' v-slot='{commands, getMarkAttrs, isActive}' v-if='!readonly'>
          <div class='menubar'>
            <!-- Format Menu Dropdown -->
            <button class='dropdown' v-on:click.prevent="showFormatMenu=!showFormatMenu">
              <span v-if='isActive.paragraph()'>Paragraph</span>
              <span v-else-if='isActive.heading({level:1})'>Heading 1</span>
              <span v-else-if='isActive.heading({level:2})'>Heading 2</span>
              <span v-else-if='isActive.heading({level:3})'>Heading 3</span>
              <span v-else-if='isActive.code_block()'>Code Block</span>
              <span v-else>Format</span> <i class='mdi mdi-menu-down'></i>
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
            <button :class='{"active":isActive.bold()}' @click='commands.bold'><i class='mdi mdi-format-bold'></i></button>
            <button :class='{"active":isActive.italic()}' @click='commands.italic'><i class='mdi mdi-format-italic'></i></button>
            <button :class='{"active":isActive.underline()}' @click='commands.underline'><i class='mdi mdi-format-underline'></i></button>
            <div class='sep'></div>
            <button :class='{"active":isActive.bullet_list()}' @click='commands.bullet_list'><i class='mdi mdi-format-list-bulleted'></i></button>
            <button :class='{"active":isActive.ordered_list()}' @click='commands.ordered_list'><i class='mdi mdi-format-list-numbered'></i></button>
            <div class='sep'></div>
            <button :class='{"active":isActive.link()}' @click='toggleLinkMenu(getMarkAttrs("link"))'><i class='mdi mdi-link'></i></button>
            <button :class='{"active":isActive.blockquote()}' @click='commands.blockquote'><i class='mdi mdi-format-quote-close'></i></button>
            <button :class='{"active":isActive.code()}' @click='commands.code'><i class='mdi mdi-code-tags'></i></button>
            <!-- <div class='sep'></div> -->
            <!-- <button><i class='mdi mdi-file-code-outline'></i></button> -->
            <!-- <button @click='commands.undo'><i class='mdi mdi-undo'></i></button> -->
            <!-- <button @click='commands.redo'><i class='mdi mdi-redo'></i></button> -->
            <button @click='save' style='float:right;'><span>Save</span></button>
            <!-- Link Form -->
            <div class='link-form' v-if='showLinkMenu'>
              <input type='text' name='url' v-model='linkUrl' ref='linkInput' placeholder='https://' spellcheck='false' autocomplete='off'
                @keydown.enter.prevent='setLinkUrl(commands.link, linkUrl)'
                @keydown.esc='hideLinkMenu'
                @click='$refs.linkInput.focus()'/>
              <button @click='setLinkUrl(commands.link, "")' style='margin-left:5px; font-size:14px;'>Clear</button>
            </div>
          </div>
        </editor-menu-bar>
        <!-- Content -->
        <h1>
          <input name='title' v-model='note.title' :readonly=readonly />
          <span>{{note.created | formatDate('MMM DD, YYYY')}}
            <input name='tags' placeholder='tags' v-model='note.tags' :readonly=readonly /></span>
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
  import {Blockquote, BulletList, CodeBlock, HardBreak, Heading, ListItem,
    OrderedList, TodoItem, TodoList, Bold, Code, Italic, Link, Strike,
    Underline, History} from 'tiptap-extensions';
  import {buildquery} from '@/utils/utils';
  import {sync} from 'vuex-pathify';

  var QUERY_SAVENOTE = `mutation saveNote {
    saveNote(id:{id}, title:{title}, tags:{tags}, body:{body}) {
      note { id slug title tags body created }
      success
    }}`;

  export default {
    name: 'Notes',
    components: {Navigation, Footer, Search, EditorContent, EditorMenuBar},
    computed: { ...sync('notes/*') },
    data: () => ({
      readonly: true,
      linkUrl: null,
      showLinkMenu: false,
      showFormatMenu: false,
    }),

    created: function() {
      // Tiptap Examples: https://github.com/scrumpy/tiptap
      // Tiptap Documentation: https://tiptap.scrumpy.io/docs
      this.$store.set('global/layout', 'topnav');
      this.editor = new Editor({
        extensions: [new Blockquote(), new BulletList(), new CodeBlock(), new HardBreak(),
          new Heading({levels: [1, 2, 3]}), new ListItem(), new OrderedList(), new TodoItem(),
          new TodoList(), new Link(), new Bold(), new Code(), new Italic(), new Strike(),
          new Underline(), new History(),
        ],
        editable: false,
      });
    },

    methods: {
      // Save - Save the current Title and Content to the server
      save: function() {
        console.log('save');
        let self = this;
        let data = {id:self.note.id, title:self.note.title,
          tags:self.note.tags, body:self.editor.getHTML()};
        let request = buildquery(QUERY_SAVENOTE, data);
        request.xhr.then(function(response) {
          console.log(response);
        });
      },

      // Toggle Link Menu - Show or hide the link menu input
      // see also: https://tiptap.scrumpy.io/links
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

      // Hide Link Menu - Hide the link menu without changing anything
      hideLinkMenu: function() {
        this.linkUrl = null;
        this.showLinkMenu = false;
      },

      // Set Link URL - Set the link URL then hide the link menu
      setLinkUrl: function(command, url) {
        command({href: url});
        this.hideLinkMenu();
      },
    },

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
        border-radius: 5px;
        border: 0px;
        box-shadow: none;
        padding: 2px 5px;
        cursor: pointer;
        font-size: 20px;
        margin-right: 5px;
        line-height: 23px;
        width: auto;
        span { font-size: 16px; }
        i.mdi { position:relative; top:1px; }
        &:hover { background-color: lighten($darkbg-color, 8%); }
        &.active { background-color: lighten($darkbg-color, 16%); }
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
        width: 130px;
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

    .note {
      width: 800px;
      margin: 20px auto;
      padding-top: 60px;
      min-height: calc(100vh - 70px);
    }
    
    input[name=title] {
      background-color: transparent;
      border-width: 0px;
      border-radius: 0px;
      font-size: 40px;
      font-weight: 600;
      margin: 5px 0px 5px -2px;
      padding: 0px;
      text-transform: uppercase;
      white-space: normal;
      line-height: 40px;
    }
    input[name=tags] {
      background-color: transparent;
      border-width: 0px;
      border-radius: 0px;
      font-size: 16px;
      font-weight: 400;
      width: 600px;
      padding: 0px 0px 3px 10px;
    }
  }
</style>
