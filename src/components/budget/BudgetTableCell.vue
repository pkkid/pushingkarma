<template>
  <td :class='[cls,{editing}]'>
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
          this.$emit('changed', {...data, callback:function(success) {
            self.editing = false;
            console.log(success);
            if (success) { self.value = newvalue; }
          }});
        }
      },
    }
  };
</script>

<style lang='scss'>

</style>
