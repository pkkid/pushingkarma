<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>{{month.format('MMMM YYYY')}} Budget
        <div style='float:right'>
          <i class='mdi mdi-chevron-left' @click.prevent='month = month.add(-1, "month")'/>
          <i class='mdi mdi-chevron-right' @click.prevent='month = month.add(1, "month")'/>
          <b-button :class='{"active":month != today}' @click.prevent='month = today'>Today</b-button>
        </div>
        <div class='subtext'>View {{loading ? '' : count}} {{month.format('MMMM')}} transactions</div>
      </h1>
      <div style='clear:both'/>
      <div v-if='!loading' v-hotkey='keymap'>
        <div id='rightpanel'>
          <div id='monthdetails'>
            <div class='header'>{{month.format('MMMM')}} Spending Overview</div>
            <dl class='spending'>
              <dt>Income</dt><dd class='blur'>{{this.income|usdint}}</dd>
              <dt>Spent</dt><dd class='blur'>{{this.spent|usdint}}</dd>
              <dt>Remaining</dt><dd class='total' :class='amountcls(this.income + this.spent)'>{{this.income + this.spent|usdint}}</dd>
            </dl>
            <hr/>
            <dl class='comments'>
              <template v-for='(amount,comment) in this.comments'>
                <template v-if='(amount < -100) || (amount > 100)'>
                  <dt :key='comment + "_label"'>{{comment}}</dt>
                  <dd :key='comment' class='blur'>{{amount|usdint}}</dd>
                </template>
              </template>
            </dl>
          </div>
          <div id='monthdetails' style='margin-top:20px;'>
            <div class='header'>Total Spending History</div>
            <canvas id='spendchart'/>
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
  import Chart from 'chart.js/auto';
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
      transactions: [],     // List of transactions in current view
      tablerows: null,      // Row items to display
      spendchart: null,     // Chart.js Spend Chart
      // Smmary data
      count: 0,             // Total transactions in view
      income: 0,            // Total income this month
      spent: 0,             // Total spent this month
      remaining: 0,         // Total remaining this month
      comments: [],         // Summarized comments
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
      history: pathify.sync('budget/history'),
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

      // Amount Class
      // Red Green or Regular class style
      amountcls: function(amount) {
        return amount > 0 ? 'gtzero blur' : 'ltzero blur';
      },

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
        try {
          this.cancelsearch = api.cancel(this.cancelsearch);
          var token = this.cancelsearch.token;
          var datestr = this.month.format('MMM YYYY');
          var params = {search:`date="${datestr}"`, limit:9999};
          var {data} = await api.Budget.getTransactions(params, token);
          this.transactions = data.results;
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
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

      // Populate Tablerows
      populateTablerows: function() {
        this.tablerows = this.initTablerows();
        var catnames = Object.keys(this.tablerows);
        for (var trx of this.transactions) {
          var amount = parseFloat(trx.amount);
          var cat = trx.category || butils.UNCATEGORIZED;
          if (catnames.indexOf(cat.name) == -1) { continue; }
          this.tablerows[cat.name].count += 1;
          this.tablerows[cat.name].items.push(trx);
          this.tablerows[cat.name].total += amount;
          this.tablerows[butils.TOTAL.name].total += amount;
        }
        // Remove empty rows
        for (var key of Object.keys(this.tablerows)) {
          if (this.tablerows[key].total == 0) { delete this.tablerows[key]; }
        }
      },

      // Populate Month Data
      populateMonthData: function() {
        this.count = 0;
        this.income = 0;
        this.spent = 0;
        this.comments = new utils.DefaultDict(Number);
        var catnames = Object.keys(this.tablerows);
        for (var trx of this.transactions) {
          var amount = parseFloat(trx.amount);
          var cat = trx.category || butils.UNCATEGORIZED;
          this.count += 1;
          if (catnames.indexOf(cat.name) == -1) { continue; }
          this.income += cat.name == 'Income' ? amount : 0;
          this.spent += cat.name != 'Income' ? amount : 0;
          if (trx.comment) { this.comments[trx.comment] += amount; }
        }
        // Sort comments by -amount
        this.comments = fromPairs(sortBy(toPairs(this.comments), 1));
      },

      initChart: function() {
        if (this.spendchart === null) {
          var ctx = document.getElementById('spendchart');
          var opts = {};
          utils.rset(opts, 'type', 'line');
          utils.rset(opts, 'data.labels', ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
          utils.rset(opts, 'data.datasets', []);
          utils.rset(opts, 'data.datasets.0.backgroundColor', 'rgba(200, 0, 0, 1)');
          utils.rset(opts, 'data.datasets.0.borderColor', 'rgba(200, 0, 0, 1)');
          utils.rset(opts, 'data.datasets.0.label', '2021');
          utils.rset(opts, 'data.datasets.0.tension', 0.2);
          utils.rset(opts, 'data.datasets.1.backgroundColor', 'rgba(200, 0, 0, 0.2)');
          utils.rset(opts, 'data.datasets.1.borderColor', 'rgba(200, 0, 0, 0.2)');
          utils.rset(opts, 'data.datasets.1.label', '2020');
          utils.rset(opts, 'data.datasets.1.tension', 0.2);
          utils.rset(opts, 'options.elements.point.radius', 0);
          utils.rset(opts, 'options.plugins.legend.display', false);
          utils.rset(opts, 'options.plugins.tooltip.displayColors', false);
          utils.rset(opts, 'options.plugins.tooltip.intersect', false);
          utils.rset(opts, 'options.plugins.tooltip.mode', 'index');
          utils.rset(opts, 'options.plugins.tooltip.position', 'nearest');
          utils.rset(opts, 'options.scales.x.grid.display', false);
          utils.rset(opts, 'options.scales.x.ticks.font.size', 9);
          utils.rset(opts, 'options.scales.y.grid.color', '#ddd');
          utils.rset(opts, 'options.scales.y.ticks.font.size', 9);
          // Callbacks
          utils.rset(opts, 'options.scales.x.ticks.callback', function(value) {
            if ([0,2,4,6,8,10].indexOf(value) != -1) { return opts.data.labels[value]; }
            return '';
          });
          utils.rset(opts, 'options.scales.y.ticks.callback', function(value) {
            if (Math.abs(value) < 5) { return ''; }
            if ((value > 0) && (value < 1000)) { return `$${value}`; }
            if ((value > 0) && (value < 1000000)) { return `$${parseInt(value/1000)}k`; }
            if ((value < 0) && (value > -999)) { return `-$${parseInt((value*-1))}`; }
            if ((value < 0) && (value > -999999)) { return `-$${parseInt((value*-1)/1000)}k`; }
            return value;
          });
          this.spendchart = new Chart(ctx, opts);
        }
      },

      updateChart: function(category) {
        this.initChart();
        category = category === undefined ? 'Total' : category;
        this.spendchart.data.datasets[0].data = this.history[category][2021];
        this.spendchart.data.datasets[1].data = this.history[category][2020];
        this.spendchart.update();
      },

      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function() {
        await this.getTransactions();
        this.populateTablerows();
        this.populateMonthData();
        this.loading = false;
        await this.$nextTick();
        this.updateChart();
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
    // Previous and Next month buttons
    h1 .mdi:hover {
      cursor: pointer;
      background-color: rgba(0,0,0,0.05); 
      border-radius: 3px;
      user-select: none;
    }
    h1 button {
      padding: 20px 10px;
      margin-top: 5px;
      border-width: 0px;
      background-color: transparent;
      font-weight: bold;
      &:hover { background-color: rgba(0,0,0,0.05); }
    }

    // Category table
    .tablewrap { width: 542px; }
    .totalrow { font-weight:600; background-color:$lightbg-bg1; }
    .diffbar {
      position: relative;
      top: 5px;
      .bg { width: 140px; height:10px; background-color:#ddd; border-radius:3px; position:absolute; }
      .amt { min-width:0px; max-width:140px; height:10px; background-color:#58881b; border-radius:3px; position:absolute;
        background:linear-gradient(90deg, #58881b 0%, #58881b 100px, #9d0006 100px, #9d0006 100%); }
      .line { width: 1px; height:10px; background-color:#f2f2f2; position:absolute; left:99px; }
    }

    // Side panel
    #rightpanel {
      float: right;
      width: 370px;
    }
    #monthdetails {
      border: 1px solid $lightbg-bg3;
      background-color:  lighten($lightbg-bg1, 2%);
      border-radius: 3px;
      padding: 1px;
      .header {
        font-size: 12px;
        font-weight: 600;
        background-color: $lightbg-bg2;
        line-height: 22px;
        padding: 0px 10px;
      }
      .spending {
        font-size: 0.95em;
        padding: 0px 10px;
        dt { width: 100px; }
        dd { margin-left:270px; text-align:right; width:70px; }
        dd.gtzero { color:$lightbg-green2; font-weight:bold; }
        dd.ltzero { color:$lightbg-red1; font-weight:bold; }
        .total { border-top: 1px solid $lightbg-fg4; }
      }
      hr { margin:10px auto; }
      .comments {
        opacity: 0.8;
        padding: 0px 10px;
        dt { width: 260px; }
        dd { margin-left:270px; text-align:right; width:70px; }
      }
    }
    #spendchart {
      height: 250px;
      margin: 10px 5px;
      width: 100%;
    }

  }
</style>
