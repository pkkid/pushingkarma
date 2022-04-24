<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>{{month.format('MMMM YYYY')}} Budget
        <div style='float:right'>
          <div class='lwrap'><b-loading class='is-small' :active='loading' :is-full-page='false'/></div>
          <b-button @click.prevent='setMonth(month.add(-1, "month"))'><i class='mdi mdi-chevron-left'/></b-button>
          <b-button :disabled='month.format("YYYY-MM") >= today.format("YYYY-MM")' @click.prevent='setMonth(month.add(1, "month"))'><i class='mdi mdi-chevron-right'/></b-button>
          <b-button :disabled='month.format("YYYY-MM") == today.format("YYYY-MM")' @click.prevent='setMonth(today)'>Today</b-button>
        </div>
        <div class='subtext'>
          <a href='#' @click='showTransactions'>Showing {{loading ? '' : count}} {{month.format('MMMM')}} transactions</a>
        </div>
      </h1>
      <div style='clear:both'/>
      <div v-if='true' v-hotkey='keymap'>
        <div id='rightpanel'>
          <div id='monthdetails'>
            <div class='header'>{{month.format('MMMM')}} Spending Overview</div>
            <dl class='spending'>
              <dt>Income</dt><dd class='blur'>{{this.income|usdint}}</dd>
              <dt>Spent</dt><dd class='blur'>{{this.spent|usdint}}</dd>
              <dt>Remaining</dt><dd class='total' :class='amountcls(this.income + this.spent)'>{{this.income + this.spent|usdint}}</dd>
            </dl>
            <hr v-if='numcomments'/>
            <dl class='comments' v-if='numcomments'>
              <template v-for='(amount,comment) in this.comments'>
                <dt :key='comment + "_label"'>{{comment}}</dt>
                <dd :key='comment' class='blur'>{{amount|usdint}}</dd>
              </template>
            </dl>
          </div>
          <div id='monthdetails' style='margin-top:20px;'>
            <div class='header'>{{category}} Spending History</div>
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
        <div style='clear:both;'></div>
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
      category: 'Total Spending', // Category displayed on chart
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
      history: pathify.sync('budget/history'),
      search: pathify.sync('budget/search'),
      view: pathify.sync('budget/view'),
      columns: function() { return this.initColumns(); },
      items: function() { return this.tablerows; },
      keymap: function() { return {
        ...this.tableMixinKeymap(),
        'shift+left': () => this.setMonth(this.month.add(-1, "month")),
        'shift+right': () => this.setMonth(this.month.add(1, "month")),
      };},
      numcomments: function() { return Object.keys(this.comments).length; },
    },
    watch: {
      month: function() { this.refresh(); },
    },
    mounted: function() {
      this.today = dayjs(dayjs().format('YYYY-MM'));
      this.month = dayjs(this.$route.query.month || this.today);
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

      // Update chart on new focus
      newFocus: function(tabindex, newcell) {
        var category = tabindex === null ? undefined : newcell.row.name;
        category = category == 'Uncategorized' ? undefined : category;
        this.chartjs_update(category);
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
        // Remove totals < $100 and sort by amount
        // eslint-disable-next-line no-unused-vars
        this.comments = Object.filter(this.comments, ([k,v]) => Math.abs(v) >= 100);
        this.comments = fromPairs(sortBy(toPairs(this.comments), 1));
      },

      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function() {
        this.loading = true;
        await this.getTransactions();
        document.title = `PK - ${this.month.format('MMMM')} Budget`;
        this.populateTablerows();
        this.populateMonthData();
        await this.$nextTick();
        this.chartjs_update();
        setTimeout(() => this.loading = false, 300);
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

      // Show Transactions
      // load the current months individual transactions
      showTransactions: function() {
        var datestr = this.month.format('MMM YYYY');
        this.search = `date="${datestr}"`;
        this.view = 'transactions';
      },

      // Set Month
      // Set the current month to display
      setMonth: function(month) {
        var monthstr = month.format('YYYY-MM');
        var todaystr = this.today.format('YYYY-MM');
        if (monthstr <= todaystr) {
          this.month = month;
          var urlvalue = monthstr == todaystr ? null : monthstr;
          utils.updateHistory(this.$router, {month:urlvalue});
          this.refresh();
        }
      },

      // Chart.js Init
      // Initialize the chartjs history display
      chartjs_init: function() {
        // Register new function to place tooltip
        const tooltipPlugin = Chart.registry.getPlugin('tooltip');
        tooltipPlugin.positioners.custom = function(_, pos) {
          if (pos === false) { return false; }
          const chart = this._chart;
          return {x:pos.x, y:chart.chartArea.top-10};
        };
        // Create the Chart
        if (this.spendchart === null) {
          var elem = document.getElementById('spendchart');
          var opts = {};
          utils.rset(opts, 'type', 'line');
          utils.rset(opts, 'data.labels', ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
          utils.rset(opts, 'data.datasets', []);
          utils.rset(opts, 'data.datasets.0.label', '2021');
          utils.rset(opts, 'data.datasets.0.tension', 0.2);
          utils.rset(opts, 'data.datasets.1.label', '2020');
          utils.rset(opts, 'data.datasets.1.tension', 0.2);
          utils.rset(opts, 'options.elements.point.radius', 0);
          utils.rset(opts, 'options.plugins.legend.display', false);
          utils.rset(opts, 'options.plugins.tooltip.bodySpacing', 0);
          utils.rset(opts, 'options.plugins.tooltip.callbacks.label', this.chartjs_tooltip_label);
          utils.rset(opts, 'options.plugins.tooltip.caretSize', 0);
          utils.rset(opts, 'options.plugins.tooltip.displayColors', false);
          utils.rset(opts, 'options.plugins.tooltip.intersect', false);
          utils.rset(opts, 'options.plugins.tooltip.mode', 'index');
          utils.rset(opts, 'options.plugins.tooltip.position', 'custom');
          utils.rset(opts, 'options.plugins.tooltip.titleMarginBottom', 2);
          utils.rset(opts, 'options.scales.x.grid.display', false);
          utils.rset(opts, 'options.scales.x.ticks.callback', this.chartjs_xticks);
          utils.rset(opts, 'options.scales.x.ticks.font.size', 9);
          utils.rset(opts, 'options.scales.y.grid.color', this.chartjs_ygridcolor);
          utils.rset(opts, 'options.scales.y.grid.drawTicks', false);
          utils.rset(opts, 'options.scales.y.ticks.callback', this.chartjs_yticks);
          utils.rset(opts, 'options.scales.y.ticks.font.size', 9);
          utils.rset(opts, 'plugins', []);
          utils.rset(opts, 'plugins.0.afterLayout', this.chartjs_plugin_linecolor);
          utils.rset(opts, 'plugins.1.afterDatasetsDraw', this.chartjs_plugin_drawmonth);
          this.spendchart = new Chart(elem, opts);
        }
      },

      chartjs_update: function(category) {
        this.chartjs_init();
        this.category = category === undefined ? 'Total' : category;
        this.spendchart.data.datasets[0].data = this.history[this.category][2021];
        this.spendchart.data.datasets[1].data = this.history[this.category][2020];
        this.spendchart.update();
      },

      // Chart.js X Ticks
      // Callback function for x ticks display
      chartjs_xticks: function(value) {
        if (this.spendchart === null) { return ''; }
        if ([0,2,4,6,8,10].indexOf(value) != -1) { return this.spendchart.data.labels[value]; }
        return '';
      },

      // Chart.js Y Grid Color
      // Callback function for y grid color
      chartjs_ygridcolor: function(ctx) {
        return ctx.tick.value == 0 ? '#bbb' : 'transparent';
      },

      // Chart.js Y Ticks
      // Callback function for y ticks display
      chartjs_yticks: function(value) {
        if (this.spendchart === null) { return ''; }
        const y = this.spendchart.scales.y;
        if ((value != y.max) && (value != y.min) && (value != 0)) { return ''; }
        if (value == 0) { return '$0'; }
        if ((value > 0) && (value < 1000)) { return `$${Math.round(value)}`; }
        if ((value > 0) && (value < 1000000)) { return `$${Math.round(value/100)/10}k`; }
        if ((value < 0) && (value > -999)) { return `-$${Math.round(value*-1)}`; }
        if ((value < 0) && (value > -999999)) { return `-$${Math.round((value*-1)/100)/10}k`; }
        return value;
      },

      // Chart.js Plugin Linecolor
      // Sets the line color to greene above 0, red below.
      chartjs_plugin_linecolor: function(chart) {
        // Gradient is based on the percent of the canvas with 0% being the top. We
        // need to do a bunch of math here to determine what percent of the canvas
        // the zero line is located at.
        const y = chart.scales.y;
        const numtotal = y.end - y.start;
        const numpctzero = 1 - ((numtotal - y.end) / numtotal);
        // Add a subtle fade as we transition from red to green
        const gmin = Math.min(Math.max(numpctzero, 0), 1);
        const gmax = Math.min(Math.max(numpctzero+0.04, 0), 1);
        // Update first dataset (this year)
        const gradient0 = chart.ctx.createLinearGradient(0, y.top, 0, y.bottom);
        gradient0.addColorStop(0, 'rgba(118,111,106,1)');
        gradient0.addColorStop(gmin, 'rgba(118,111,106,1)');
        gradient0.addColorStop(gmax, 'rgba(157,0,6,1)');
        gradient0.addColorStop(1, 'rgba(157,0,6,1)');
        chart.data.datasets[0].borderColor = gradient0;
        // Update second dataset (last year)
        const gradient1 = chart.ctx.createLinearGradient(0, y.top, 0, y.bottom);
        gradient1.addColorStop(0, 'rgba(118,111,106,0.2)');
        gradient1.addColorStop(gmin, 'rgba(118,111,106,0.2)');
        gradient1.addColorStop(gmax, 'rgba(157,0,6,0.2)');
        gradient1.addColorStop(1, 'rgba(157,0,6,0.2)');
        chart.data.datasets[1].borderColor = gradient1;
      },

      // Chart.js Plugin Draw Month
      // Draw the current month or month mouse is hovered over
      chartjs_plugin_drawmonth: function(chart) {
        var activepoint = chart.tooltip._active[0];
        var index = parseInt(this.month.format('MM')) - 1;
        var numlabels = (chart.data.labels.length - 1);
        if (activepoint) { index = activepoint.index; }
        const scale = (chart.chartArea.right - chart.chartArea.left) / numlabels;
        const px = (index * scale) + chart.chartArea.left;
        chart.ctx.beginPath();
        chart.ctx.strokeStyle = '#666';
        chart.ctx.setLineDash([5,5]);
        chart.ctx.moveTo(px, chart.chartArea.top);
        chart.ctx.lineTo(px, chart.chartArea.bottom);
        chart.ctx.stroke();
        chart.ctx.setLineDash([1,0]);
      },

      chartjs_tooltip_label: function(ctx) {
        return `${ctx.dataset.label}: ${utils.usdint(ctx.parsed.y)}`;
      },

    }
  };
</script>

<style lang='scss'>
  #budgetmonth {
    // Previous and Next month buttons
    h1 button,
    h1 .loading {
      padding: 0px 10px;
      line-height: 40px;
      height: 40px;
      margin-top: 5px;
      border-width: 0px;
      background-color: transparent;
      font-weight: bold;
      outline: none;
      box-shadow: none;
      &:hover { background-color: rgba(0,0,0,0.05); }
      .mdi { font-size:1.5em; }
    }
    h1 .lwrap { display:inline-flex; position:relative; width:20px; height:35px; margin-top:7px; margin-right:10px; }
    //h1 .loading-overlay { display:inline-flex; width:20px; height:35px; }

    // Category table
    $amtbg: desaturate($lightbg-fg4, 5%);  // #766F6A rgb(118,111,106)
    .tablewrap { width: 542px; }
    .totalrow { font-weight:600; background-color:$lightbg-bg1; }
    .diffbar {
      position: relative;
      top: 7px;
      .bg { width: 140px; height:6px; background-color:#ddd; border-radius:3px; position:absolute; }
      .amt { min-width:0px; max-width:140px; height:6px; background-color:$amtbg; border-radius:3px; position:absolute;
        background:linear-gradient(90deg, $amtbg 0%, $amtbg 100px, $lightbg-red1 100px, $lightbg-red1 100%); }
      .line { width: 1px; height:6px; background-color:#f2f2f2; position:absolute; left:99px; }
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
