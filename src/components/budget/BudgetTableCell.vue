<template>
  <td :class='[cls,{editing}]'>
    <input v-if='editing' type='text' :value='value' @blur='save' ref='input'/>
    <div v-else @dblclick.prevent='edit'>{{value}}</div>
  </td>
</template>

<script>
  import Vue from 'vue';

  export default {
    name: 'BudgetTableCell',
    props: {
      cls: {default: ''},
      editable: {default: false},
      init: {default: null},
      selectall: {default: false},
      type: {default: 'string'},
    },
    data: () => ({
      value: null,
      editing: false,
    }),
    created: function() {
      this.value = this.init;
    },
    methods: {
      // Edit
      // Enable editing the selected cell.
      edit: async function() {
        console.log('edit');
        if (this.editable) {
          this.editing = this.editable;
          await Vue.nextTick();
          if (this.selectall) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },

      // Save
      // Stop editing and save the specified value.
      save: function() {
        // this.editing = false;
      },
    }
  };
</script>

<style lang='scss'>

</style>
