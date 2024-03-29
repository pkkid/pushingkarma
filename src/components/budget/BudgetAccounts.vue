<template>
  <div id='budgetsettingsaccounts' v-hotkey='keymap'>
    <!-- <h2>Bank Accounts</h2> -->
    <p>Add all accounts that you plan to upload .qfx files for. Each bank should
      provide a unique FID that you can see by opening the file. This is used to
      determine the bank the data originated when uploading transactions.</p>
    <div v-click-outside='cancelAll'>
      <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
        <template slot-scope='props'>
          <b-table-column v-for='cell in props.row' :key='cell.col.name' :label='cell.col.label' :width='cell.col.width' :numeric='cell.col.numeric' :class='cell.col.cls'>
            <TableCell v-bind='cell' :ref='`c${cell.tabindex}`' :key='cell.row.id' @click.native='click($event, cell.tabindex)'/>
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
  import {TYPES} from '@/components/TableMixin';
  import TableMixin from '@/components/TableMixin';

  export default {
    name: 'BudgetAccounts',
    mixins: [TableMixin],
    data: () => { return {
      columns: [
        {type:TYPES.editable, label:'Name', field:'name', width:160},
        {type:TYPES.editable, label:'FID', field:'fid', select:true, width:160},
        {type:TYPES.editable, label:'Payee Field', field:'payee', width:160},
        {label:'Last Updated', field:'balancedt', width:140, format:utils.timeAgo},
        {label:'Transactions', field:'meta.num_transactions', width:150, numeric:true, format:utils.intComma},
        {label:'Balance', field:'balance', width:150, cls:'blur', numeric:true, format:utils.usd, opts:{color:true}},
      ],
    };},
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tableMixinKeymap(); },
    },
    mounted: function() {
      document.title = `PK - Budget Accounts`;
    },
    methods: {
      // Save
      // Save the current cell value - There is a slight bit of wonkyness here in
      // that this function is called anytime a cell value changed, but depending
      // on the state of row.id or row.name we may be creating or deleting the
      // the account data.
      save: async function(id, field, newvalue, cell=null, refresh=false) {
        if (id == null && field == 'name' && newvalue != '') { return this.create(newvalue); }
        if (id == null && field == 'name' && newvalue == '') { return this.refresh(); }
        try {
          var change = utils.rset({}, field, newvalue);
          var {data} = await api.Budget.patchAccount(id, change);
          this.updateItem(id, data);
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
          this.$set(this.items, this.items.length-1, data);
        } catch(err) {
          utils.snackbar(`Error creating account ${name}.`);
          console.error(err);
        }
      },

      // Confirm Delete
      // Confirm and delete an existing account in the database
      confirmDelete: async function() {
        var self = this;
        var account = this.getCell().row;
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
