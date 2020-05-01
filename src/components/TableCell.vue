<template>
  <div class='tablecell' :class='[status,{focused,editing}]'>
    <div v-if='cls=="check"' @mousedown='preventDoubleClick' ref='div' tabindex='-1'>
      <i v-if='value' class='mdi mdi-check'/></div>
    <div v-else :value='data.value' v-html='displayValue' :contenteditable='contenteditable' ref='div' 
      spellcheck='false' @input="$emit('input', $event.target.textContent)" tabindex='-1'/>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';
  var CLASSES_NOT_EDITABLE = ['check'];

  export default {
    name: 'TableCell',
    props: {
      data: Object,         // Data {name, field, value, etc}
      focus: Number,        // Global tabindex of focused cell
      editing: Boolean,     // Globally True when editing a value
    },
    data: () => ({
      status: 'default',    // Sets bgcolor to status {success or error}
    }),
    computed: {
      // Passed in data properties
      row: function() { return this.data.row; },                              // Item row index
      id: function() { return this.data.id; },                                // Column Name
      field: function() { return this.data.field; },                          // Field Name
      value: function() { return this.data.value; },                          // Cell value
      name: function() { return this.data.name || null; },                    // Column Name
      cls: function() { return this.data.cls; },                              // Class applied to cell
      display: function() { return this.data.display || null; },              // Display callback
      select: function() { return this.data.select || null; },                // Select text when editing
      tabindex: function() { return this.data.tabindex || null; },            // Global ID (for editable cells)
      contenteditable: function() { return this.focused && this.editing; },   // True if currently editable
      editable: function() { return this.data.editable && !CLASSES_NOT_EDITABLE.includes(this.cls); },
      focused: function() { return (this.tabindex && (this.tabindex === this.focus)); },
      displayValue: function() { return this.display ? this.display(this.value) : this.value; },
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
          if (!this.select) { range.collapse(false); }
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
      border-radius: 4px;
      border: 0px;
      border: 2px solid transparent;
      box-sizing: border-box;
      font-size: 0.9em;
      line-height: 24px;
      margin: 0px;
      padding: 1px 3px;
      width: 100%;
      height: 29px;
      transition: all .3s ease;
    }
    &.focused div {
      background-color: $lightbg-bg2;
      border: 2px solid darken($lightbg-bg2, 3%);
    }
    &.focused.editing div {
      background-color: $lightbg-bg2;
      border: 2px solid $lightbg-blue0;
      box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
      color: darken($lightbg-blue0, 50%);
    }
    &.success div {
      background-color: desaturate(lighten($darkbg-blue0, 40%), 10%);
    }
    &.error div {
      background-color: desaturate(lighten($darkbg-red0, 40%), 10%);
      border-color: $darkbg-red0;
    }
  }
</style>
