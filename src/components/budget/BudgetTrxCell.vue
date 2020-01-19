<template>
  <td :class='[display,status]' class='trxcell'>
    <!-- Display input or div -->
    <input v-if='editing' type='text' ref='input' v-model='value'
      @focus.prevent='oldvalue=$event.target.value' v-click-outside='save' 
      @keyup.enter.prevent='save'
      @keyup.esc.prevent='cancel'
      @keyup.up.prevent='setHighlighted(-1)'
      @keyup.down.prevent='setHighlighted(+1)'/>
    <div v-else-if='display == "usdint"' @dblclick.prevent='edit'>{{value | usdint}}</div>
    <div v-else @dblclick.prevent='edit'>{{value}}</div>
    <!-- Display choices if applicable -->
    <ul v-if='showchoices' class='choices'>
      <li v-for='(c, i) in fchoices' :key='c.id' class='choice'
        :class='{highlighted:i==highlighted}'>
        {{c.name}}
      </li>
    </ul>
  </td>
</template>

<script>
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  import fuzzysort from 'fuzzysort';
  import Vue from 'vue';

  // Status names
  var DEFAULT = 'default';            // Default display
  var EDITING = 'editing';            // Displays input for editing
  var SAVING = 'saving';              // Blue background when saving
  var ERROR = 'error';                // Red background on error
  
  export default {
    name: 'BudgetTableCell',
    props: {
      item: {default: {}},            // Trx this cell represents
      name: {default: ''},            // Item field.name for cell
      choices: {default: () => []},   // Selectable choices
      display: {default: ''},         // Display type: usdint, bool
      editable: {type: Boolean},      // Cell id editable
      selectall: {type: Boolean},     // Selectall text when editing
    },
    data: () => ({
      status: 'default',              // See constants above
      oldvalue: null,                 // Cached value determines if changes made
      value: null,                    // Current value of this cell
      highlighted: 0,                 // Current highlighted choice
    }),
    computed: {
      editing: function() { return this.status == EDITING; },
      showchoices: function() { return this.editing && this.fchoices.length; },
      lowerchoices: function() { return this.choices.map(c => c.name.toLowerCase()); },
      fchoices: function() {
        if (!this.editing) { return []; }
        if (this.value == '') { return this.choices; }
        if (this.lowerchoices.indexOf(this.value.toLowerCase()) >= 0) { return []; }
        var result = fuzzysort.go(this.value, this.choices, {key:'name'});
        return result.map(x => x.obj);
      },
    },
    mounted: function() {
      this.value = utils.rget(this.item, this.name);
      if (this.display == 'bool') { this.value = this.value ? 'x' : '-'; }
      this.cls = this.name.replace(/\./g, '_');
    },

    methods: {
      // Edit
      // Enable editing the selected cell.
      edit: async function() {
        if (this.editable) {
          this.status = this.editable ? EDITING : DEFAULT;
          await Vue.nextTick();
          if (this.selectall) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },

      // Cancel
      // Cancel the current edits
      cancel: async function() {
        this.value = this.oldvalue;
        await Vue.nextTick();
        this.status = this.DEFAULT;
      },

      // Save
      // Emit an event if the specified value changed
      save: async function(event) {
        if (event.target.className == 'choice') {
          this.value = _.trim(event.target.textContent);
        } else if (this.fchoices.length) {
          this.value = _.trim(this.fchoices[this.highlighted].name);
        } else if (this.value != this.oldvalue) {
          try {
            var change = utils.rset({}, this.name.replace('.','_'), this.value);
            var {data} = await api.Budget.patchTransaction(this.item.id, change);
            this.status = SAVING;
            this.$emit('updated', data);
            this.value = this.value;
            setTimeout(() => this.status = this.DEFAULT, 500);
          } catch(err) {
            this.status = ERROR;
          }
        } else {
          this.status = DEFAULT;
        }
      },

      // Set Highlighted
      // Adjust highlighted choice by offset (for next / prev selection).
      setHighlighted: function(offset) {
        var newvalue = this.highlighted + offset;
        newvalue = Math.max(newvalue, 0);
        newvalue = Math.min(newvalue, this.fchoices.length - 1);
        this.highlighted = newvalue;
      },

    }
  };
</script>

<style lang='scss'>
  .trxcell {
    position: relative;
    ul.choices {
      background-color: #eee;
      border-radius: 2px;
      border: 1px solid #ddd;
      left: 5px;
      overflow: hidden;
      padding: 3px 0px;
      position: absolute;
      top: 17px;
      width: calc(100% - 10px);
      z-index: 90;
      li.choice {
        line-height: 22px;
        list-style-type: none;
        margin: 0px;
        padding: 0px 5px;
        &.highlighted { background-color: #ddd; }
      }
    }
  }
  
</style>
