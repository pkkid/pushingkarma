<template>
  <div id='budgetsettingsaccounts' v-hotkey='keymap'>
    <h2>Bank Accounts</h2>
    <p>Add all accounts that you plan to upload .qfx files for. Each bank should
      provide a unique FID that you can see by opening the file. This is used to
      determine the bank the data originated when uploading transactions.</p>
    <div v-click-outside='cancelAll'>
      <b-table :data='tabledata' :narrowed='true'>
        <template slot-scope='props'>
          <b-table-column v-for='c in props.row' :key='c.name' :label='c.name' :width='c.width'
            :numeric='c.numeric' :cell-class='c.class'>
            <TableCell v-bind='{data:c, focus, editing}' :ref='`c${c.tabindex}`'
              @click.native='clickSetFocus($event, c.tabindex)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
      <div style='margin-top:10px;'>
        <b-button size='is-small' type='is-danger' class='is-pulled-right' @click.prevent='confirmDelete' :disabled='!focus'>Delete Account</b-button>
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
    name: 'BudgetSettingsAccounts',
    mixins: [TableMixin],
    data: () => ({
      columns: [
        {name:'Name', field:'name', editable:true, width:'30%'},
        {name:'FID', field:'fid', editable:true, select:true, width:'30%'},
        {name:'Last Updated', field:'balancedt', width:'20%', display:utils.timeAgo},
        {name:'Balance', field:'balance', display:utils.usd, numeric:true, width:'20%', class:'blur'},
      ],
    }),
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
    methods: {
      // Add
      // Add new row to populate, not yet saved to the db.
      add: function() {
        this.items.push({});
        this.setFocusLast();
      },
      
      // Save
      // Save the current cell value - There is a slight bit of wonkyness here in
      // that this function is called anytime a cell value changed, but depending
      // on the state of cell.id or cell.name we may be creating or deleting the
      // the account data.
      save: async function(event, tabindex) {
        var cell = this.getCell(tabindex);
        var newvalue = cell.getNewValue();
        if (cell.id == null && cell.field == 'name' && newvalue != '') { return this.create(newvalue); }
        if (cell.id == null && cell.field == 'name' && newvalue == '') { return this.refresh(); }
        if (newvalue != cell.value) {
          try {
            var change = utils.rset({}, cell.field, newvalue);
            var {data} = await api.Budget.patchAccount(cell.id, change);
            Vue.set(this.items, cell.row, data);
            cell.setStatus('success', 1000);
          } catch(err) {
            cell.setStatus('error');
            utils.snackbar(`Error saving ${this.name}.`);
            console.log(err);
          }
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
        var cell = this.cell;
        var account = this.getRowData(cell);
        this.$buefy.dialog.confirm({
            title: 'Delete Account',
            message: `Are you sure you want to delete the account <b>${account.name}</b>?`,
            confirmText: 'Delete Account',
            focusOn: 'cancel',
            type: 'is-danger',
            onConfirm: () => this.actuallyDelete(account),
        });
      },

      // Actually Delete
      // Delete the specified account
      actuallyDelete: async function(account) {
        await api.Budget.deleteAccount(account.id);
        utils.snackbar(`Successfully deleted account ${account.name}.`);
        this.refresh();
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
