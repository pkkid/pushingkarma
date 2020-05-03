<template>
  <div id='budgetsettingsaccounts' v-hotkey='keymap'>
    <!-- <h2>Bank Accounts</h2> -->
    <p>Add all accounts that you plan to upload .qfx files for. Each bank should
      provide a unique FID that you can see by opening the file. This is used to
      determine the bank the data originated when uploading transactions.</p>
    <div v-click-outside='cancelAll'>
      <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
        <template slot-scope='props'>
          <b-table-column v-for='c in props.row' :key='c.name' :label='c.name' :width='c.width'
            :numeric='c.numeric' :header-class='c.cls' :cell-class='c.cls'>
            <TableCell :data='c' :ref='`c${c.tabindex}`' @click.native='clickSetFocus($event, c.tabindex)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
      <div style='margin-top:10px;'>
        <b-button size='is-small' type='is-danger' class='is-pulled-right' @click.prevent='confirmDelete'
          :disabled='!focus'>Delete Account</b-button>
        <b-button size='is-small' class='add' @click.prevent='add'>Add New Account</b-button>
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
    name: 'BudgetAccounts',
    mixins: [TableMixin],
    data: function() {
      return {
        columns: [
          // Columns should add up to 884px wide
          {name:'Name', field:'name', editable:true, width:'200px'},
          {name:'FID', field:'fid', editable:true, select:true, width:'200px'},
          {name:'Last Updated', field:'balancedt', width:'150px', display:utils.timeAgo},
          {name:'Transactions', field:'summary.num_transactions', width:'150px', numeric:true, display:utils.insertCommas},
          {name:'Balance', field:'balance', width:'184px', cls:'blur', numeric:true, display:utils.usd},
        ],
      };
    },
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
    methods: {
      // Save
      // Save the current cell value - There is a slight bit of wonkyness here in
      // that this function is called anytime a cell value changed, but depending
      // on the state of cell.id or cell.name we may be creating or deleting the
      // the account data.
      save: async function(cell, id, row, field, newvalue, refresh=false) {
        if (id == null && field == 'name' && newvalue != '') { return this.create(newvalue); }
        if (id == null && field == 'name' && newvalue == '') { return this.refresh(); }
        try {
          var change = utils.rset({}, field, newvalue);
          var {data} = await api.Budget.patchAccount(id, change);
          Vue.set(this.items, row, data);
          if (cell) { cell.setStatus('success', 1000); }
          if (refresh) { this.refresh(); }
        } catch(err) {
          if (cell) { cell.setStatus('error'); }
          utils.snackbar(`Error saving account.`);
          console.log(err);
        }
      },

      // Create
      // Create a new account in the database
      create: async function(name) {
        try {
          var params = {name:name, type:'bank'};
          var {data} = await api.Budget.createAccount(params);
          Vue.set(this.items, this.items.length-1, data);
          console.log(data);
        } catch(err) {
          utils.snackbar(`Error creating account ${name}.`);
          console.error(err);
        }
      },

      // Confirm Delete
      // Confirm and delete an existing account in the database
      confirmDelete: async function() {
        var self = this;
        var cell = this.cell;
        var account = this.getRowData(cell);
        this.$buefy.dialog.confirm({
            title: 'Delete Account',
            message: `Are you sure you want to delete the account <b>${account.name}</b>?`,
            confirmText: 'Delete Account',
            focusOn: 'cancel',
            type: 'is-danger',
            onConfirm: async function() {
              await api.Budget.deleteAccount(account.id);
              utils.snackbar(`Successfully deleted account ${account.name}.`);
              self.refresh();
            },
        });
      },

      // Refresh
      // Refresh the list of accounts displayed
      refresh: async function() {
        var {data} = await api.Budget.getAccounts();
        this.items = data.results;
      },
    }
  };
</script>
