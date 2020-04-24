<template>
  <div id='budgetmonth' v-hotkey='keymap'>
    <h2>Budget Settings</h2>
    <div class='contentwrap'>
      <h3>Accounts</h3>
      <b-table :data='tabledata' :narrowed='true' :hoverable='true' v-click-outside='cancelAll'>
        <template slot-scope='props'>
          <b-table-column v-for='data in props.row' :key='props.index+data.field' :label='data.name'>
            <TableCell v-bind='{data, focus, editing}' :ref='`c${data.tabindex}`' @click.native='clickSetFocus($event, data.tabindex)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
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
    name: 'BudgetSettings',
    mixins: [TableMixin],
    data: () => ({
      columns: [
        {name:'Name', field:'name', editable:true},
        {name:'FID', field:'fid', editable:true, select:true},
        {name:'Balance', field:'balance', display:utils.usd},
        {name:'Last Transaction', field:'none'},
      ],
    }),
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
    methods: {
      save: async function(event, tabindex) {
        var cell = this.$refs[`c${tabindex}`][0];
        var newvalue = event.srcElement.value;
        if (newvalue != cell.value) {
          var change = utils.rset({}, cell.field, newvalue);
          console.log(`Updating account ${cell.id}`, change); 
          var {data} = await api.Budget.patchAccount(cell.id, change);
          // console.log(data);
          console.log(cell.row, data);
          Vue.set(this.items, cell.row, data);
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .contentwrap {
      background-color: white;
      border: 1px solid darken($lightbg-bg3, 10%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 40px;
    }

  }
</style>
