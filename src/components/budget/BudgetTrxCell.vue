<template>
  <td :class='[display,status]' class='trxcell'>
    <!-- Display input or div -->
    <input v-if='status == EDITING' type='text' ref='input' v-model='value'
      @focus.prevent='oldvalue=$event.target.value' @blur='save'/>
    <div v-else-if='display == "usdint"' @dblclick.prevent='edit'>{{value | usdint}}</div>
    <div v-else @dblclick.prevent='edit'>{{value}}</div>
    <!-- Display choices if applicable -->
    <ul v-if='fchoices.length && status == EDITING' class='choices'>
      <li v-for='choice in fchoices' :key='choice'>{{choice}}</li>
    </ul>
  </td>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  import fuzzysort from 'fuzzysort';
  import Vue from 'vue';
  
  export default {
    name: 'BudgetTableCell',
    props: {
      item: {default: {}},          // Trx this cell represents
      name: {default: ''},          // Item field.name for cell
      choices: {default: null},     // Selectable choices
      display: {default: ''},       // Display type: usdint, bool
      editable: {type: Boolean},    // Cell id editable
      selectall: {type: Boolean},   // Selectall text when editing
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
      // Managing choices
      lchoices: null,               // Lowercase choices (for lookup)
      ichoices: null,               // Choice items for fuzzysort
      fchoices: [],                 // Filtered choices for display
    }),
    mounted: function() {
      this.value = utils.rget(this.item, this.name);
      if (this.display == 'bool') { this.value = this.value ? 'x' : '-'; }
      this.cls = this.name.replace(/\./g, '_');
      if (this.choices) {
        this.lchoices = this.choices.map(c => c.toLowerCase());
        this.ichoices = this.choices.map(c => {return {name:c};});  
      }
    },

    watch: {
      // Watch Value
      // Filter displayed choices from entered value (if applicable)
      value: function(value) {
        if ((this.choices) && (this.status == this.EDITING)) {
          if (this.value == '') {
            this.fchoices = this.choices;
          } else if (this.lchoices.indexOf(value) >= 0) {
            this.fchoices = [];
          } else {
            var result = fuzzysort.go(value, this.ichoices, {key:'name'});
            this.fchoices = result.map(x => x.target);
          }
        }
      },
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
      save: async function() {
        if (this.value != this.oldvalue) {
          try {
            var change = {[this.name]: this.value};
            var {data} = await api.Budget.patchTransaction(this.item.id, change);
            this.status = this.SAVING;
            this.$emit('updated', data);
            this.value = this.value;
            setTimeout(() => this.status = this.DEFAULT, 500);
          } catch(err) {
            this.status = this.ERROR;
          }
        } else {
          this.status = this.DEFAULT;
        }
      },

    }
  };
</script>

<style lang='scss'>
  .trxcell {
    position: relative;
    ul.choices {
      position: absolute;
      top: 17px;
      left: 5px;
      width: calc(100% - 10px);
      background-color: #eee;
      border: 1px solid #ddd;
      border-radius: 2px;
      overflow: hidden;
      z-index: 90;
    }
  }
  
</style>
