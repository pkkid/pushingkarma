<template>
  <div id='notes' v-hotkey='keymap'>
    <Navigation :cls="'topnav'" />
    <div class='sidebar'>
      <Search ref='search'/>
    </div>
    <div class='content'>
      <div class='note' :class='{editable:editing}'>
        <MenuBar ref='menubar' />
        <h1><input name='title' autocomplete='off' v-model='note.title' :readonly=!editing />
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
  import MenuBar from './NotesMenuBar';
  import Search from './NotesSearch';
  import {EditorContent} from 'tiptap';
  import {sync} from 'vuex-pathify';

  export default {
    name: 'Notes',
    components: {Navigation, Footer, MenuBar, Search, EditorContent},
    computed: {
      editing: sync('notes/editing'),
      editor: sync('notes/editor'),
      note: sync('notes/note'),
      keymap: function() { return {
        'f1': (e) => this.$refs.search.focus(e),
        'e': (e) => this.$refs.menubar.startEditing(e),
        'ctrl+s': (e) => this.$refs.menubar.save(e),
        'esc': (e) => this.$refs.menubar.stopEditing(e),
      };},
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
    //background-color: $lightbg-color;
    box-sizing: border-box;
    color: $lightbg-text;
    margin-left: 300px;
    padding: 60px 20px 40px 20px;
    background-color: darken($lightbg-color, 10%);
    
    // General Note Display
    .note {
      width: 900px;
      margin: 20px auto;
      position: relative;
      min-height: calc(100vh - 70px);
      transition: padding 0.2s ease;
      margin-top: 50px;
      border: 1px solid darken($lightbg-color, 20%);
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 10px 50px;
      background-color: $lightbg-color;
      //&.editable { padding-top: 60px; }
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
  }
</style>
