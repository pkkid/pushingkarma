<template>
  <div class='tablecell' :class='[{focused,editing}]'>
    <div :contenteditable='editable' ref='div' spellcheck='false'>{{displayValue}}</div>
  </div>
</template>

<script>
  import Vue from 'vue';

  export default {
    name: 'TableCell',
    props: {
      data: Object,       // Data {name, field, value, etc}
      focus: Number,      // Global tabindex of focused cell
      editing: Boolean,   // Globally True when editing a value
    },
    computed: {
      row: function() { return this.data.row; },                      // Item row index
      id: function() { return this.data.id; },                        // Column Name
      field: function() { return this.data.field; },                  // Field Name
      value: function() { return this.data.value; },                  // Cell value
      name: function() { return this.data.name || null; },            // Column Name
      display: function() { return this.data.display || null; },      // Display callback
      select: function() { return this.data.select || null; },        // Select text when editing
      tabindex: function() { return this.data.tabindex || null; },    // Global ID (for editable cells)
      editable: function() { return this.focused && this.editing; },
      focused: function() { return (this.tabindex && (this.tabindex === this.focus)); },
      displayValue: function() { return this.display ? this.display(this.value) : this.value; },
    },
    watch: {
      editing: async function(newvalue, oldvalue) {
        if (this.focused && newvalue && !oldvalue) {
          await Vue.nextTick();
          var range = document.createRange();
          range.selectNodeContents(this.$refs.div);
          var selection = window.getSelection();
          if (!this.select) { range.collapse(false); }
          selection.removeAllRanges();
          selection.addRange(range);
        }
      },
    }
  };
</script>

<style lang='scss'>
  .tablecell {
    div, input {
      background-color: transparent;
      border-radius: 4px;
      border: 0px;
      border: 2px solid transparent;
      box-sizing: border-box;
      color: $lightbg-fg1;
      font-size: 0.9em;
      line-height: 24px;
      margin: 0px;
      padding: 1px 3px;
      width: 100%;
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
  }
</style>
