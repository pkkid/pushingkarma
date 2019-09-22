<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'><Search/></div>
    <div class='content'>
      <div class='note'>
        <editor-menu-bar :editor="editor" v-slot="{commands, isActive, focused}">
          <div class="menubar is-hidden" :class="{'is-focused': focused}">
            <button :class='{"active":isActive.bold()}' @click='commands.bold'><i class='mdi mdi-format-bold'></i></button>
            <button :class='{"active":isActive.italic()}' @click='commands.italic'><i class='mdi mdi-format-italic'></i></button>
            <button :class='{"active":isActive.underline()}' @click='commands.underline'><i class='mdi mdi-format-underline'></i></button>
            <button :class='{"active":isActive.code()}' @click='commands.code'><i class='mdi mdi-code-not-equal-variant'></i></button>
            <button :class='{"active":isActive.paragraph()}' @click='commands.paragraph'><i class='mdi mdi-format-paragraph'></i></button>
            <button :class='{"active":isActive.heading({level:1})}' @click='commands.heading({level:1})'><i class='mdi mdi-format-header-1'></i></button>
            <button :class='{"active":isActive.heading({level:2})}' @click='commands.heading({level:2})'><i class='mdi mdi-format-header-2'></i></button>
            <button :class='{"active":isActive.heading({level:3})}' @click='commands.heading({level:3})'><i class='mdi mdi-format-header-3'></i></button>
            <button :class='{"active":isActive.bullet_list()}' @click='commands.bullet_list'><i class='mdi mdi-format-list-bulleted'></i></button>
            <button :class='{"active":isActive.ordered_list()}' @click='commands.ordered_list'><i class='mdi mdi-format-list-numbered'></i></button>
            <button :class='{"active":isActive.blockquote()}' @click='commands.blockquote'><i class='mdi mdi-format-quote-close'></i></button>
            <button :class='{"active":isActive.code_block()}' @click='commands.code_block'><i class='mdi mdi-code-tags'></i></button>
            <button><i class='mdi mdi-file-code-outline'></i></button>
            <button @click='commands.undo'><i class='mdi mdi-undo'></i></button>
            <button @click='commands.redo'><i class='mdi mdi-redo'></i></button>
            <button @click='save'>Save</button>
          </div>
        </editor-menu-bar>
        <input name='title' v-model='note.title'/>
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
    saveNote(id:{id}, title:{title}, body:{body}) {
      note { id slug title body tags created }
      success
    }}`;

  export default {
    name: 'Notes',
    components: {Navigation, Footer, Search, EditorContent, EditorMenuBar},
    computed: { ...sync('notes/*') },

    mounted: function() {
      // Tiptap Examples: https://github.com/scrumpy/tiptap
      // Tiptap Documentation: https://tiptap.scrumpy.io/docs
      this.$store.set('global/layout', 'topnav');
      this.editor = new Editor({
        extensions: [new Blockquote(), new BulletList(), new CodeBlock(), new HardBreak(),
          new Heading({levels: [1, 2, 3]}), new ListItem(), new OrderedList(), new TodoItem(),
          new TodoList(), new Link(), new Bold(), new Code(), new Italic(), new Strike(),
          new Underline(), new History(),
        ],
        editable: true,
        content: '<p>This is just a boring paragraph</p>',
      });
    },

    methods: {
      save: function() {
        console.log('save');
        let self = this;
        let data = {id:self.note.id, title:self.note.title, body:self.note.body};
        let request = buildquery(QUERY_SAVENOTE, data);
        request.xhr.then(function(response) {
          console.log(response);
        });
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
    .note {
      width: 900px;
      margin: 20px auto;
      min-height: calc(100vh - 70px);
    }

    button {
      background-color: darken($lightbg-color, 1%);
      background-image: none;
      border-radius: 5px;
      border: 0px;
      color: $lightbg-text-dim;
      cursor: pointer;
      font-size: 20px;
      margin-right: 5px;
      width: auto;
      &:hover { background-color: darken($lightbg-color, 4%); }
      &.active { background-color: darken($lightbg-color, 8%); }
    }
  }
</style>
