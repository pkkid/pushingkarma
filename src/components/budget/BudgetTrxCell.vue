<template>
  <td :class='[display,status,{cursor:cursor==cell}]' class='trxcell' @click='click'>
    <input v-if='showinput' type='text' ref='input' v-model='value'
      @keyup.up.prevent='setHighlighted(-1)'	
      @keyup.down.prevent='setHighlighted(+1)'
      @keydown.enter='pickChoice'/>
    <div v-else-if='display == "usdint"' class='blur'>{{value | usdint}}</div>
    <div v-else>{{value}}</div>
    <ul v-if='showchoices' class='choices'>
      <li v-for='(c, i) in fchoices' :key='c.id' class='choice'
        :class='{highlighted:i==highlighted}' @click='pickChoice'>{{c.name}}</li>
    </ul>
  </td>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  import * as pathify from 'vuex-pathify';
  import fuzzysort from 'fuzzysort';
  import trim from 'lodash/trim';
  import Vue from 'vue';

  // Status names
  var DEFAULT = 'default';            // Default display
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
      cell: {default: 'x'},           // Cell ID
    },
    data: () => ({
      status: 'default',              // See constants above
      oldvalue: null,                 // Cached value determines if changes made
      value: null,                    // Current value of this cell
      highlighted: 0,                 // Current highlighted choice
    }),
    computed: {
      cursor: pathify.sync('budget/cursor'),
      selected: pathify.sync('budget/selected'),
      editing: pathify.sync('budget/editing'),
      bool: function() { return this.display == 'bool'; },
      showinput: function() { return this.editing == true && this.cursor == this.cell; },
      lowerchoices: function() { return this.choices.map(c => c.name.toLowerCase()); },
      showchoices: function() { return this.editing && this.fchoices.length; },
      fchoices: function() {
        if (!this.editing) { return []; }
        if (this.cursor != this.cell) { return []; }
        if ((this.value == '') || !this.value) { return this.choices; }
        if (this.lowerchoices.indexOf(this.value.toLowerCase()) >= 0) { return []; }
        var result = fuzzysort.go(this.value, this.choices, {key:'name'});
        return result.map(x => x.obj);
      },
      sendvalue: function() {
        if (this.bool) { return utils.strToBool(this.value) ? true : false; }
        return this.value;
      },
    },
    mounted: function() {
      this.setValue(this.item);
      this.cls = this.name.replace(/\./g, '_');
    },

    methods: {
      // Click: Click a non-editing cell
      click: function() {
        var cell = this.cell;
        if (this.cursor == this.cell) {
          this.edit();
        } else if (this.editable) {
          this.editing = false;
          this.cursor = cell;
          this.selected.push(cell);
        }
      },
      
      // Pick Choice
      // If there are dropdown choices shown, this picks the currently
      // selected choice, populating the input field with the correct text.
      pickChoice: async function(event) {
        if (this.fchoices.length) {
          event.preventDefault();
          event.stopPropagation();
          if (event.target.className == 'choice') { this.value = trim(event.target.textContent); }
          else { this.value = trim(this.fchoices[this.highlighted].name); }
        }
      },

      // Edit: Enable editing the selected cell.
      edit: async function() {
        if ((this.editable) && (this.cursor == this.cell)) {
          this.oldvalue = this.value;
          this.cursor = this.cell;
          this.editing = true;
          await Vue.nextTick();
          if (this.selectall) { this.$refs.input.select(); }
          else { this.$refs.input.focus(); }
        }
      },

      // Cancel: Cancel the current edits
      cancel: function() {
        this.editing = false;
        this.status = DEFAULT;
        this.setValue(this.item);
      },

      // Save: Emit an event if the specified value changed
      save: async function() {
        if (this.value != this.oldvalue) {
          try {
            var change = utils.rset({}, this.name.replace('.','_'), this.sendvalue);
            var {data} = await api.Budget.patchTransaction(this.item.id, change);
            //this.editing = false;
            this.status = SAVING;
            this.setValue(data);
            setTimeout(() => this.status = this.DEFAULT, 500);
          } catch(err) {
            this.status = ERROR;
          }
        } else {
          this.status = DEFAULT;
          this.setValue(this.item);
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

      // Set Value
      // Set the value from the data and passed in name
      setValue: function(data) {
        this.value = utils.rget(data, this.name);
        if (this.bool) { this.value = this.value ? 'x' : '-'; }
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
