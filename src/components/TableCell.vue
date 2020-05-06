<template>
  <div class='tablecell' :class='[status,{focused,editing}]' :style='{"max-width":col.width}'>
    <div v-if='col.cls=="check"' @mousedown='preventDoubleClick' ref='div' tabindex='-1' :style='{"min-width":col.width}'>
      <i v-if='value' class='mdi mdi-check'/></div>
    <div v-else v-html='html' :contenteditable='contenteditable' ref='div' :style='{"min-width":col.width}'
      spellcheck='false' @input="text=$event.target.textContent" tabindex='-1'
      @keyup.up.prevent='moveChoice(-1)' @keyup.down.prevent='moveChoice(+1)'
      @keydown.enter='choose'/>
    <ul v-if='contenteditable && (choices.length > 0)' class='choices' :style='{"min-width":col.width}'>
      <li v-for='(c,i) in choices' :key='c.id' class='choice' :class='{highlighted:i==choice}' @click='choose'>{{c.name}}</li>
    </ul>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';
  import fuzzysort from 'fuzzysort';
  import trim from 'lodash/trim';
  var CANNOT_FREE_EDIT = ['check'];

  export default {
    name: 'TableCell',
    props: {
      col: {type:Object, required:true},
      row: {type:Object, required:true},
      rowindex: {type:Number, required:true},
      tabindex: {required:true},
    },
    data: () => ({
      choice: 0,            // Current highlighted choice
      choices: [],          // Choices for display
      editing: false,       // True if editing this cell
      focused: false,       // True if this cell is focused
      status: 'default',    // Sets bgcolor to status {success or error}
      text: '',             // Current textContent
    }),
    computed: {
      contenteditable: function() { return this.focused && this.editing; },     // True if currently editable
      item: function() { return this.row; },                                    // Alias for this.row
      value: function() { return utils.rget(this.row, this.col.field); },       // Raw value for this cell
      editable: function() { return this.col.editable && !CANNOT_FREE_EDIT.includes(this.col.cls); },
      html: function() {
        if (this.col.opts) { return this.col.display(this.value, this.col.opts); }
        if (this.col.display) { return this.col.display(this.value); }
        return this.value;
      },
    },
    mounted: function() {
      this.text = this.$refs.div.textContent;
    },
    watch: {
      // Watch Editable - Set the cursor at the end of the input
      // or select all text if the option select is true.
      contenteditable: async function() {
        if (this.contenteditable) {
          await this.$nextTick();
          var range = document.createRange();
          range.selectNodeContents(this.$refs.div);
          var selection = window.getSelection();
          if (!this.col.select) { range.collapse(false); }
          selection.removeAllRanges();
          selection.addRange(range);
          this.$refs.div.focus();
        }
      },
      text: function(value) {
        if (!this.contenteditable) { return; }
        if (!this.col.choices) { return; }
        var lchoices = this.col.choices.map(c => c.name.toLowerCase());
        if (!value || value == '') { return this.col.choices; }
        if (lchoices.indexOf(value.toLowerCase()) >= 0) { return []; }
        var result = fuzzysort.go(value, this.col.choices, {key:'name'});
        this.choices = result.map(x => x.obj);
      },
    },
    methods: {
      // Choose
      // Called when clicking a choice
      choose: function(event) {
        if (this.choices.length) {
          event.preventDefault();
          event.stopPropagation();
          var newtext;
          if (event.target.classList.contains('choice')) { newtext = trim(event.target.textContent); }
          else { newtext = trim(this.choices[this.choice].name); }
          this.$refs.div.textContent = newtext;
          this.text = newtext;
          this.choices = [];
        }
      },

      // Move Choice
      // Adjust highlighted choice by offset (for next / prev selection).
      moveChoice: function(offset) {
        var newchoice = this.choice + offset;
        newchoice = Math.max(newchoice, 0);
        newchoice = Math.min(newchoice, this.choices.length - 1);
        this.choice = newchoice;
      },

      // Set Status
      // Sets visual indicator that saving value was success or error
      setStatus: async function(status, duration=null) {
        this.status = status;
        if (duration !== null) {
          await utils.sleep(duration);
          this.status = 'fadestatus';
          await utils.sleep(1000);
          this.status = 'default';
        }
      },

      // Prevent Double Click
      // Checkmark cells need this to quickly toggle the value but
      // it often also selects a word of text which is annoying.
      preventDoubleClick: function(event) {
        if (event.detail > 1) { event.preventDefault(); }
      },
    },
  };
</script>

<style lang='scss'>
  .tablecell {
    position: relative;

    > div {
      background-color: transparent;
      border-radius: 3px;
      border: 0px;
      border: 1px solid transparent;
      box-sizing: border-box;
      font-size: 0.9em;
      line-height: 20px;
      margin: 1px 0px;
      padding: 2px 5px;
      width: 100%;
      height: 26px;
      transition: all .1s ease;
      white-space: nowrap;  // overflow editing
      overflow: hidden;  // overflow editing
      max-width: 300px;  // overflow editing
      br { display:none; }
      * { display:inline; white-space:nowrap; }
    }
    
    // Focused & Editing
    &.fadestatus div { transition: all 2s ease !important; }
    &.focused {
      div {
        background-color: darken($lightbg-bg1, 3%);
        border: 1px solid darken($lightbg-bg2, 8%);
        box-shadow:
          0 0 0 2px lighten($lightbg-bg1, 2%),
          inset 0 0 0px 1px lighten($lightbg-bg1, 1%);
        position: absolute;  // overflow editing
        max-width: fit-content;  // overflow editing
      }
      &.editing div {
        border: 1px solid $lightbg-blue1;
        color: darken($lightbg-blue0, 50%);
        box-shadow: 0 0 0 2px rgba(7, 102, 120, 0.25);
      }
    }

    // Success & Error
    &.success div {
      background-color: desaturate(lighten($darkbg-green1, 40%), 30%);
      border: 1px solid $darkbg-green1;
      box-shadow:
        0 0 0 2px lighten($lightbg-bg1, 2%),
        inset 0 0 0px 1px lighten($lightbg-bg1, 1%);
    }
    &.error div {
      background-color: desaturate(lighten($darkbg-red0, 40%), 30%);
      border-color: darken($darkbg-red0, 5%);
      box-shadow:
        0 0 0 2px lighten($lightbg-bg1, 2%),
        inset 0 0 0px 1px lighten($lightbg-bg1, 1%);
    }

    // Choices
    ul.choices {
      background-color: $lightbg-bg2;
      border-radius: 2px;
      border: 1px solid darken($lightbg-bg1, 20%);
      box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
      color: lighten($lightbg-fg2, 20%);
      font-size: 13px;
      left: 0px;
      overflow: hidden;
      padding: 3px 0px;
      position: absolute;
      top: 29px;
      width: calc(100% - 10px);
      z-index: 20;
      li.choice {
        line-height: 22px;
        list-style-type: none;
        margin: 0px;
        padding: 0px 5px;
        &.highlighted { color: #000; }
      }
    }
  }
</style>
