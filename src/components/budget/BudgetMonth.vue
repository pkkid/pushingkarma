<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>{{month.format('MMMM')}} Budget</h1>
      Hi Mom!!
      <b-loading :active='loading' :is-full-page='false'/>
    </PageWrap>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as dayjs from 'dayjs';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import PageWrap from '@/components/site/PageWrap';

  export default {
    name: 'BudgetMonth',
    components: {PageWrap},
    data: () => ({
      loading: false,       // True to show loading indicator
      month: dayjs(),       // Current month displayed (dayjs object)
      transactions: null,   // Current months transacations
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
    },
    mounted: function() {
      this.month = dayjs(dayjs().format('YYYY-MM'));
      document.title = `PK - ${this.month.format('MMMM')} Budget`;
      this.refresh();
    },
    methods: {
      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function(showLoading=false) {
        this.loading = showLoading;
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        try {
          var params = {search: this.search};
          var {data} = await api.Budget.getTransactions(params, token);
          utils.updateHistory(this.$router, {month:this.month.format('YYYY-MM')});
          this.transactions = data.results;
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        } finally {
          setTimeout(() => this.loading = false, 300);
        }
      },

    },
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .tablewrap {
      background-color: white;
      border: 1px solid darken($lightbg-bg3, 10%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 10px;
      min-width: 1000px;
    }

  }
</style>
