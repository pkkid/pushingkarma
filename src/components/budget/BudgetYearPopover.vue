<template>
  <div class="budgetyearpopover">
    <h2>{{cell.row.name}}<div class='subtext'>{{datestr}}</div></h2>
    <b-icon icon='close' size='is-small' @click.native.prevent.stop='cell.popped=false'/>
    <dl>
      <dt>Budgeted</dt><dd>{{cell.row.budget | usdint}}</dd>
      <dt>{{remainingtxt}}</dt><dd :class='remainingcls'>{{Math.abs(remaining) | usdint}}</dd>
    </dl>
    <div class='scrollwrap'>
      <table cellpadding='0' cellspacing='0'>
        <tbody>
          <tr v-for='item in items' :key='item.id'>
            <td class='date'>{{item.date | formatDate('M/D')}}</td>
            <td class='payee'>{{item.payee}}</td>
            <td class='amount'>{{item.amount}}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class='totals' v-if='items.length'>
      <div class='total' :class='hasScroll'>{{cell.value | usdint}}</div>
      <a href='#' class='count' @click='showTransactions'>{{items.length}} transactions</a>
    </div>
  </div>
</template>

<script>
  import * as dayjs from 'dayjs';
  import * as pathify from 'vuex-pathify';

  export default {
    name: 'BudgetYear',
    props: {
      cell: {type:Object, required:true},
    },
    computed: {
      search: pathify.sync('budget/search'),
      view: pathify.sync('budget/view'),
      datestr: self => dayjs(self.monthstr).format('MMMM YYYY'),
      monthstr: self => self.cell.col.monthstr,
      items: self => self.cell.row[self.monthstr].items,
      remaining: self => self.cell.row.budget - self.cell.value,
      remainingtxt: function() {
        if (this.cell.row.budget > 0)
          return this.remaining > 0 ? 'Remaining' : 'Extra';
        return this.remaining > 0 ? 'Overspent' : 'Remaining';
      },
      remainingcls: self => self.remaining > 0 ? 'ltzero' : 'gtzero',
      hasScroll: self => self.items.length >= 13 ? 'hasScroll' : '',
    },
    methods: {
      showTransactions: function() {
        var category = this.cell.row.name;
        var datestr = dayjs(this.cell.col.monthstr).format('MMM');
        this.search = `category="${category}" date=${datestr}`;
        this.view = 'transactions';
      },
    },
  };
</script>

<style lang='scss'>
#budgetyear .budgetyearpopover {
  $popover-width: 300px;
  width: $popover-width;
  min-width: $popover-width;
  left: calc(50% - 60px);
  background-color: $lightbg-bg1;

  h2 { color:$lightbg-fg0; position:relative; }
  h2:before { background-color:#d65d0e; bottom:-3px; content:' '; display:block; height:1px; position:absolute; width:50px; }
  h2 .subtext { padding:0px; margin-top:-2px; }
  .icon { position:absolute; top:10px; right:10px; cursor:pointer; opacity:0.6; transition:opacity .3s ease; }
  .icon:hover { opacity:1; }
  dl { font-size: 0.7em; }
  dd { margin-left:70px; width:60px; text-align:right; }
  dd.gtzero { color:$lightbg-green2; font-weight:bold; }
  dd.ltzero { color:$lightbg-red1; font-weight:bold; }
  table { table-layout:fixed; font-size:0.7em; }
  table td { line-height:16px; padding:0px; border-width:0px; color:$lightbg-fg3; }
  table .date { width:35px; max-width:35px; }
  table .payee { width:185px; max-width:185px; overflow:hidden; white-space:nowrap; }
  table .amount { width:60px; max-width:60px; text-align:right; font-family:$fontfamily-code; }
  .totals { font-size:0.7em; padding-top:3px;}
  .count { padding-top:1px; }
  .total { float:right; padding-right:5px; border-top:1px solid $lightbg-fg4; text-align:right; min-width:60px;}
  .total.hasScroll { margin-right:10px; }
  .scrollwrap {
    max-height: 200px;
    padding-right: 5px;
    overflow-y: auto;
    background-color: darken($lightbg-bg1, 2%);
    &::-webkit-scrollbar { width: 10px; }
    &::-webkit-scrollbar-thumb {
      background: rgba($darkbg-bg4, 0.8);
      border-radius: 5px;
      border: 2px solid $lightbg-bg1;
    }
  }
}
</style>
