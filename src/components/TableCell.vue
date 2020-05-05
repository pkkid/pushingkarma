<template>
  <div class='tablecell' :class='[status,{focused,editing}]' :style='{"max-width":col.width}'>
    <div v-if='col.cls=="check"' @mousedown='preventDoubleClick' ref='div' tabindex='-1' :style='{"min-width":col.width}'>
      <i v-if='value' class='mdi mdi-check'/></div>
    <div v-else v-html='html' :contenteditable='contenteditable' ref='div' :style='{"min-width":col.width}'
      spellcheck='false' @input="$emit('input', $event.target.textContent)" tabindex='-1'/>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';
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
      status: 'default',    // Sets bgcolor to status {success or error}
      focused: false,       // True if this cell is focused
      editing: false,       // True if editing this cell
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
    },
    methods: {
      // Get New Value
      // Return current new value
      getNewValue: function() {
        return this.$refs.div.textContent || '';
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
        box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
        color: darken($lightbg-blue0, 50%);
        box-shadow: 0 0 0 2px rgba(7, 102, 120, 0.25);
      }
    }
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
  }
</style>
