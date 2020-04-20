<template>
  <div id='budgetmonth' v-hotkey='keymap'>
    <h2>Budget Settings</h2>
    <div class='contentwrap'>
      <h3>Accounts</h3>
      <b-table :data='tabledata' :narrowed='true' :hoverable='true' v-click-outside='cancelAll'>
        <template slot-scope='props'>
          <b-table-column v-for='data in props.row' :key='props.index+data.field' :label='data.name'>
            <TableCell v-bind='{data, focus, editing}' @click.native='clickSetFocus($event, data.gid)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
    </div>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import TableMixin from '@/components/TableMixin';

  export default {
    name: 'BudgetSettings',
    mixins: [TableMixin],
    data: () => ({
      columns: [
        {name:'Name', field:'name', id:1},
        {name:'FID', field:'fid', id:2, select:true},
        {name:'Balance', field:'balance', display:utils.usd},
        {name:'Last Transaction', field:'none'},
      ],
    }),
    computed: {
      items: pathify.sync('budget/accounts'),
      keymap: function() { return this.tablemixin_keymap(); },
    },
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .contentwrap {
      background-color: white;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 40px;
    }

  }
</style>
