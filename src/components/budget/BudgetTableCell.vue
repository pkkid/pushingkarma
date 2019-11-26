<template>
  <td :class='[cls,status,{editing}]'>
    <input v-if='editing' type='text' ref='input' :value='value' 
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
      cls: null,        // static class to apply to this cell
      editing: false,   // true when editing the cell
      oldvalue: null,   // cached value to determine if changes made
      status: null,     // success or error status when saving
      value: null,      // current value of this cell
    }),
    created: function() {
      this.value = utils.rget(this.item, this.name);
      this.cls = this.name.replace(/\./g, '_');
      this.editable = this.flags.includes('editable');
      this.selectall = this.flags.includes('selectall');
      this.bool = this.flags.includes('bool');
      this.usd = this.flags.includes('usd');
    },
    // watch: {
    //   status: function() {
    //     setTimeout(() => this.status = null, 500);
    //   },
    // },
    methods: {
      // Edit
      // Enable editing the selected cell.
      edit: async function() {
        if (this.editable) {
          this.editing = this.editable;
          await Vue.nextTick();
          if (this.selectall) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },

      // Changed
      // Emit an event if the specified value changed
      changed: async function(event) {
        var self = this;
        var newvalue = event.target.value;
        if (newvalue != this.oldvalue) {
          var data = {id:this.item.id, change:{[this.name]: newvalue}};
          this.status = 'saving';
          this.$emit('changed', data, function(success) {
            self.editing = false;
            if (success) {
              self.value = newvalue;
              setTimeout(() => self.status = null, 500);
            } else {
              self.status = 'error';
            }
          });
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgettransactions {
    td.saving div {
      background-color: rgba(0,0,255,0.1);
    }
    td.error div {
      background-color:rgba(150,0,0,0.1);
    }
  }
</style>
