<template>
  <td :class='[cls,{editing}]'>
    <input v-if='editing' type='text' ref='input' v-model='value' 
      @focus.prevent='oldvalue=$event.target.value'
      @blur='changed'/>
    <div v-else @dblclick.prevent='edit'>{{value}}</div>
  </td>
</template>

<script>
  import * as utils from '@/utils/utils';
  import Vue from 'vue';
  
  export default {
    name: 'BudgetTableCell',
    props: {
      item: {default: {}},
      name: {default: ''},
      flags: {default: ''},
    },
    data: () => ({
      cls: null,
      editing: false,
      oldvalue: null,
      value: null,
    }),
    created: function() {
      this.value = utils.rget(this.item, this.name);
      this.cls = this.name.replace(/\./g, '_');
      this.editable = this.flags.includes('editable');
      this.selectall = this.flags.includes('selectall');
      this.bool = this.flags.includes('bool');
      this.usd = this.flags.includes('usd');
    },
    methods: {
      // Edit
      // Enable editing the selected cell.
      edit: async function() {
        console.log(this.item);
        if (this.editable) {
          this.editing = this.editable;
          await Vue.nextTick();
          if (this.selectall) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },

      // Changed
      // Emit an event if the specified value changed
      changed: function() {
        this.editing = false;
        if (this.value != this.oldvalue) {
          var change = {[this.name]: this.value};
          this.$emit('changed', this.item.id, change, function() {
            console.log('callback!');
          });
        }
      },
    }
  };
</script>

<style lang='scss'>

</style>
