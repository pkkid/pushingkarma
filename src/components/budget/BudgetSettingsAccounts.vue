<template>
  <div id='budgetsettingsaccounts' v-hotkey='keymap'>
    <h2>Bank Accounts</h2>
    <p>Add all accounts that you plan to upload .qfx files for. Each bank should
      provide a unique FID that you can see by opening the file. This is used to
      determine the bank the data originated when uploading transactions.</p>
    <b-table :data='tabledata' :narrowed='true' v-click-outside='cancelAll'>
      <template slot-scope='props'>
        <b-table-column v-for='c in props.row' :key='props.index+c.field' :label='c.name' :width='c.width'
          :numeric='c.numeric' :cell-class='c.class'>
          <TableCell v-bind='{data:c, focus, editing}' :ref='`c${c.tabindex}`'
             @click.native='clickSetFocus($event, c.tabindex)'/>
        </b-table-column>
      </template>
      <template slot='empty'>No items to display.</template>
    </b-table>
    <b-button size='is-small' class='add-account' @click.prevent='add'>Add New Account</b-button>
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
        {name:'Last Transaction', field:'last_transaction', width:'20%' },
        {name:'Balance', field:'balance', display:utils.usd, numeric:true, width:'20%', class:'blur'},
      ],
    }),
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
    methods: {
      add: function() {
        this.items.push({});
        // this.setFocusLast();
      },
      
      save: async function(event, tabindex) {
        var cell = this.$refs[`c${tabindex}`][0];
        var newvalue = event.srcElement.textContent;
        if (newvalue != cell.value) {
          try {
            var change = utils.rset({}, cell.field, newvalue);
            console.log(`Updating account ${cell.id}`, change); 
            var {data} = await api.Budget.patchAccount(cell.id, change);
            Vue.set(this.items, cell.row, data);
            cell.showSuccess();
          } catch(err) {
            cell.showError();
            console.log(err);
          }
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgetsettings {
    button.add-account { margin-top: 10px; }
  }
</style>
