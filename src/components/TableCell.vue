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
      focus: Number,      // Global GID of focused cell
      editing: Boolean,   // Globally True when editing a value
    },
    computed: {
      name: function() { return this.data.name || null; },          // Column Name
      field: function() { return this.data.field || null; },        // Field Name
      value: function() { return this.data.value || null; },        // Cell value
      display: function() { return this.data.display || null; },    // Display callback
      select: function() { return this.data.select || null; },      // Select text when editing
      gid: function() { return this.data.gid || null; },            // Global ID (for editable cells)
      focused: function() { return (this.gid && (this.gid === this.focus)); },
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
