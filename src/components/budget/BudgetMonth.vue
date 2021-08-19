<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>{{month.format('MMMM YYYY')}} Budget
        <div style='float:right'>
          <i class='mdi mdi-chevron-left' @click.prevent='month = month.add(-1, "month")'/>
          <i class='mdi mdi-chevron-right' @click.prevent='month = month.add(1, "month")'/>
          <b-button :class='{"active":month != today}' @click.prevent='month = today'>Today</b-button>
        </div>
        <div class='subtext'>View {{count}} {{month.format('MMMM')}} transactions</div>
      </h1>
      <div style='clear:both'/>
      <div v-if='!loading' v-hotkey='keymap'>
        <div id='monthdetails'>
          April Spending Overview
          <div>Income: {{this.income|usdint}}</div>
          <div>Spent: {{this.spent|usdint}}</div>
          <div>Remaining: {{this.income + this.spent|usdint}}</div>
          <div>
            <div v-for='(amount,comment) in this.comments' :key='comment'>
              <template v-if='(amount < -100) || (amount > 100)'>
                {{comment}}: {{amount|usdint}}
              </template>
            </div>
          </div>
        </div>
        <div class='tablewrap'>
          <div class='clickout-detector' v-click-outside='cancelAll'>
            <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
              <template slot-scope='props'>
                <b-table-column v-for='cell in props.row' :key='cell.col.label' :label='cell.col.label' :width='cell.col.width' :numeric='cell.col.numeric' :class='cell.col.cls'>
                  <TableCell v-bind='cell' :ref='`c${cell.tabindex}`' @click.native='click($event, cell.tabindex)'/>
                </b-table-column>
              </template>
              <template slot='empty'>No items to display.</template>
            </b-table>
          </div>
        </div>
      </div>
      <div v-else>
        <b-loading active :is-full-page='false'/>
      </div>
    </PageWrap>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import * as butils from '@/components/budget/BudgetUtils';

  import fromPairs from 'lodash/fromPairs';
  import sortBy from 'lodash/sortBy';
  import toPairs from 'lodash/toPairs';

  import {TYPES} from '@/components/TableMixin';
  import dayjs from 'dayjs';
  import BudgetPopover from '@/components/budget/BudgetPopover';
  import PageWrap from '@/components/site/PageWrap';
  import TableMixin from '@/components/TableMixin';

  export default {
    name: 'BudgetMonth',
    mixins: [TableMixin],
    components: {PageWrap},
    data: () => ({
      cancelsearch: null,   // Cancel search token
      loading: false,       // True to show loading indicator
      month: dayjs(),       // Current month displayed (dayjs object)
      today: dayjs(),       // Today's month
      tablerows: null,      // Row items to display
      // Smmary data
      count: 0,             // Total transactions in view
      income: 0,            // Total income this month
      spent: 0,             // Total spent this month
      remaining: 0,         // Total remaining this month
      comments: [],         // Summarized comments
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
      columns: function() { return this.initColumns(); },
      items: function() { return this.tablerows; },
      keymap: function() { return this.tableMixinKeymap(); },
    },
    watch: {
      month: function() { this.refresh(); },
    },
    mounted: function() {
      this.month = dayjs(dayjs().format('YYYY-MM'));
      this.today = dayjs(dayjs().format('YYYY-MM'));
      document.title = `PK - ${this.month.format('MMMM')} Budget`;
      this.refresh();
    },
    methods: {
      // Difference Bar
      // HTML for the difference column on the table
      diffbar: function(value, row) {
        var amt = ((row.total / row.budget) * 100); 
        return `
          <div class="diffbar">
            <div class="bg"></div>
            <div class="amt" style="width: ${amt}px"></div>
            <div class="line"></div>
          </div>`;
      },

      // Get Transactions
      // Search for and update the list of displayed transactions
      getTransactions: async function() {
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        var datestr = this.month.format('MMM YYYY');
        var params = {search:`date="${datestr}"`, limit:9999};
        var {data} = await api.Budget.getTransactions(params, token);
        return data.results;
      },

      // Init Columns
      // Initialize table columns
      initColumns: function() {
        var columns = [];
        var opts = {color:true, symbol:'$'};
        var monthstr = this.month.format('YYYY-MM');
        columns.push({type:TYPES.editable, label:'Category', field:'name', width:180});
        columns.push({type:TYPES.editable, label:'Budget', field:'budget', width:100, opts:opts, numeric:true, format:utils.usdint, cls:'blur'});
        columns.push({type:TYPES.popover, label:'Spent', field:'total', width:100, opts:opts, numeric:true, format:utils.usdint, cls:'blur', monthstr:monthstr, popoverComponent:BudgetPopover});
        columns.push({type:TYPES.readonly, label:'Difference', field:'diff', width:150, html:this.diffbar});
        return columns;
      },

      // Init Table Rows
      // Initialize an empty group collection
      initTablerows: function() {
        var tablerows = {};
        var categories = this.categories.slice();  // clone array
        categories.push(butils.UNCATEGORIZED);
        categories.push(butils.TOTAL);
        for (var cat of categories) {
          if (cat.exclude_budget == true) { continue; }
          tablerows[cat.name] = {};
          tablerows[cat.name].id = cat.id;
          tablerows[cat.name].name = cat.name;
          tablerows[cat.name].budget = cat.budget;
          tablerows[cat.name].total = 0;
          tablerows[cat.name].average = 0;
          tablerows[cat.name].count = 0;
          tablerows[cat.name].items = [];
          if (cat.meta) { tablerows[cat.name].meta = cat.meta; }
        }
        return tablerows;
      },

      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function() {
        this.loading = true;
        try {
          var transactions = await this.getTransactions();
          var tablerows = this.initTablerows();
          var categories = Object.keys(tablerows);
          // Organize the transactions into their categories
          this.count = 0;
          this.income = 0;
          this.spent = 0;
          this.comments = new utils.DefaultDict(Number);
          for (var trx of transactions) {
            var amount = parseFloat(trx.amount);
            var cat = trx.category || butils.UNCATEGORIZED;
            if (categories.indexOf(cat.name) == -1) { continue; }
            // Table data
            tablerows[cat.name].count += 1;
            tablerows[cat.name].items.push(trx);
            tablerows[cat.name].total += amount;
            tablerows[butils.TOTAL.name].total += amount;
            // Summary data
            this.count += 1;
            this.income += cat.name == 'Income' ? amount : 0;
            this.spent += cat.name != 'Income' ? amount : 0;
            if (trx.comment) { this.comments[trx.comment] += amount; }
          }
          // Remove empty rows
          for (var key of Object.keys(tablerows)) {
            if (tablerows[key].total == 0) { delete tablerows[key]; }
          }
          this.tablerows = tablerows;
          utils.updateHistory(this.$router, {search:this.search});
          this.comments = fromPairs(sortBy(toPairs(this.comments), 1));
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        } finally {
          setTimeout(() => this.loading = false, 300);
        }
      },

      // Save
      // Save the current cell value
      save: async function(id, field, newvalue, cell=null) {
        try {
          var change = utils.rset({}, field, newvalue);
          var {data} = await api.Budget.patchCategory(id, change);
          if (cell) { cell.setStatus('success', 1000); }
          return data;
        } catch(err) {
          if (cell) { cell.setStatus('error'); }
          utils.snackbar(`Error saving category.`);
          console.log(err);
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgetmonth {
    
    #monthdetails {
      float: right;
      width: 370px;
      border: 1px solid #e1e1e1;
      background-color: #f3f3f3;
      border-radius: 3px;
      padding: 5px 10px;
    }
    
    .tablewrap { width: 542px; }
    .totalrow { font-weight:600; background-color:$lightbg-bg1; }
    .diffbar {
      position: relative;
      top: 5px;
      .bg { width: 140px; height:10px; background-color:#ddd; border-radius:3px; position:absolute; }
      .amt { min-width:0px; max-width:140px; height:10px; background-color:#58881b; border-radius:3px; position:absolute;
        background:linear-gradient(90deg, #58881b 0%, #58881b 98px, #9d0006 106px, #9d0006 100%); }
      .line { width: 1px; height:10px; background-color:#f2f2f2; position:absolute; left:99px; }
    }

    H1 .mdi:hover { cursor:pointer; background-color:rgba(0,0,0,0.05);  border-radius:3px; user-select:none; }
  }
</style>
