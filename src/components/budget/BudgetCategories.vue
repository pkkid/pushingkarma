<template>
  <div id='budgetsettingscategories' v-hotkey='keymap'>
    <!-- <h2>Categories</h2> -->
    <p>Create and configure categories to bucket all transactions into. The budget
      value is used to help target an estimated amount per month to spend. Use
      shift+up and shift+down to sort items.</p>
    <div v-click-outside='cancelAll'>
      <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
        <template slot-scope='props'>
          <b-table-column v-for='cell in props.row' :key='cell.col.name' v-bind='cell.col'>
            <TableCell v-bind='cell' :ref='`c${cell.tabindex}`' :key='cell.row.id'
              @click.native='clickSetFocus($event, cell.tabindex)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
      <div style='margin-top:10px;'>
        <b-button size='is-small' type='is-danger' class='is-pulled-right' @click.prevent='confirmDelete'
          :disabled='!focus'>Delete Category</b-button>
        <b-button size='is-small' class='add' @click.prevent='add'>Add New Category</b-button>
      </div>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import TableMixin from '@/components/TableMixin';
  import Vue from 'vue';

  export default {
    name: 'BudgetCategories',
    mixins: [TableMixin],
    data: function() {
      return {
        sortfield: 'sortindex',
        columns: [
          {label:'Name', field:'name', editable:true, width:'250px'},
          {label:'Budget', field:'budget', display:utils.usdint, opts:{color:true}, select:true,
            numeric:true, editable:true, width:'100px', cls:'blur'},
          {label:'Exclude From Budget', field:'exclude_budget', cls:'check', editable:true, width:'180px'},
          {label:'Year Transactions', field:'meta.year_transactions', width:'120px', numeric:true, display:utils.intComma},
          {label:'Monthly Average', field:'meta.year_average', width:'135px', numeric:true, display:utils.usd, opts:{color:true}},
          {label:'Year Total', field:'meta.year_total', width:'135px', numeric:true, display:utils.usd, opts:{color:true}},
        ],
      };
    },
    computed: {
      items: pathify.sync('budget/categories'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
    mounted: function() {
      document.title = `PushingKarma - Budget Categories`;
    },
    methods: {
      // Save
      // Save the current cell value - There is a slight bit of wonkyness here in
      // that this function is called anytime a cell value changed, but depending
      // on the state of row.id or row.name we may be creating or deleting the
      // the category data.
      save: async function(id, rowindex, field, newvalue, cell=null, refresh=false) {
        if (id == null && field == 'name' && newvalue != '') { return this.create(newvalue); }
        if (id == null && field == 'name' && newvalue == '') { return this.refresh(); }
        try {
          var change = utils.rset({}, field, newvalue);
          var {data} = await api.Budget.patchCategory(id, change);
          Vue.set(this.items, rowindex, data);
          if (cell) { cell.setStatus('success', 1000); }
          if (refresh) { await this.refresh(); }
          return data;
        } catch(err) {
          if (cell) { cell.setStatus('error'); }
          utils.snackbar(`Error saving category.`);
          console.log(err);
        }
      },

      // Create
      // Create a new category in the database
      create: async function(name) {
        try {
          var params = {name:name, budget:0};
          var {data} = await api.Budget.createCategory(params);
          Vue.set(this.items, this.items.length-1, data);
        } catch(err) {
          utils.snackbar(`Error creating category ${name}.`);
          console.error(err);
        }
      },

      // Confirm Delete
      // Confirm and delete an existing category in the database
      confirmDelete: async function() {
        var self = this;
        var category = this.item;
        this.$buefy.dialog.confirm({
            title: 'Delete Category',
            message: `Are you sure you want to delete the category <b>${category.name}</b>?`,
            confirmText: 'Delete Category',
            focusOn: 'cancel',
            type: 'is-danger',
            onConfirm: async function() {
              await api.Budget.deleteCategory(category.id);
              utils.snackbar(`Successfully deleted category ${category.name}.`);
              self.refresh();
            },
        });
      },

      // Refresh
      // Refresh the list of categories displayed
      refresh: async function() {
        var {data} = await api.Budget.getCategories();
        this.items = data.results;
      },
    }
  };
</script>
