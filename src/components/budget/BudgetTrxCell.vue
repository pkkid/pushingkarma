<template>
  <td :class='[display,status]'>
    <input v-if='status == EDITING' type='text' ref='input' :value='value' 
      @focus.prevent='oldvalue=$event.target.value'
      @blur='changed'/>
    <div v-else-if='display == "usdint"' @dblclick.prevent='edit'>{{value | usdint}}</div>
    <div v-else @dblclick.prevent='edit'>{{value}}</div>
  </td>
</template>

<script>
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import Vue from 'vue';
  
  export default {
    name: 'BudgetTableCell',
    props: {
      item: {default: {}},          // Trx this cell represents
      name: {default: ''},          // Item field.name for cell
      display: {default: ''},       // Display type: usdint, bool
      editable: {type: Boolean},    // cell id editable
      selectall: {type: Boolean},   // selectall text when editing
    },
    data: () => ({
      // Status constants
      DEFAULT: 'default',           // Default display
      EDITING: 'editing',           // Displays input for editing
      SAVING: 'saving',             // Blue background when saving
      ERROR: 'error',               // Red background on error
      // Class variables
      status: 'default',            // See constants above
      oldvalue: null,               // Cached value determines if changes made
      value: null,                  // Current value of this cell
    }),
    computed: {
      transactions: pathify.sync('budget/transactions'),
    },
    created: function() {
      this.value = utils.rget(this.item, this.name);
      if (this.display == 'bool') { this.value = this.value ? 'x' : '-'; }
      this.cls = this.name.replace(/\./g, '_');
    },
    methods: {
      // Edit
      // Enable editing the selected cell.
      edit: async function() {
        if (this.editable) {
          this.status = this.editable ? this.EDITING : this.DEFAULT;
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
          try {
            this.status = this.SAVING;
            var change = {[this.name]: newvalue};
            var {data} = await api.Budget.patchTransaction(this.item.id, change);
            var i = _.findIndex(this.transactions, {id:data.id});
            Vue.set(this.transactions, i, data);
            self.value = newvalue;
            setTimeout(() => self.status = this.DEFAULT, 500);
          } catch(err) {
            self.status = this.ERROR;
          }
        } else {
          this.status = this.DEFAULT;
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgettransactions {
    td.saving div { background-color: rgba(0,0,255,0.1); }
    td.error div { background-color:rgba(150,0,0,0.1); }
  }
</style>
