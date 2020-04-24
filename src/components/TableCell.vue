<template>
  <div :class='[{focused}]'>
    <input v-if='showinput' type='text' ref='input' :value='value'/>
    <div v-else>{{displayValue}}</div>
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
      focused: function() { return (this.tabindex && (this.tabindex === this.focus)); },
      showinput: function() { return this.focused && this.editing; },
      displayValue: function() { return this.display ? this.display(this.value) : this.value; },
    },
    watch: {
      editing: async function(newvalue, oldvalue) {
        if (this.focused && newvalue && !oldvalue) {
          await Vue.nextTick();
          if (this.select) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },
    }
  };
</script>

<style lang='scss'>
  .focused {
    background-color: red;
  }
</style>
