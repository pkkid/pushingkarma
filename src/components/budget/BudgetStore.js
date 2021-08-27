
export default {
  account: null,        // One of {null, <account>}
  accounts: [],         // List of accounts [{id, name, fid, type, balance, balancedt, payee, url}, ...]
  categories: [],       // List of categories [{id, name, budget, sortindex, comment, url}, ...]
  search: null,         // Current search string
  summary: null,        // Summary of transacations for a few date ranges
  history: null,        // History spending
  demo: false,          // Set true to hide sensative values
  view: 'month',        // One of {budget, transactions}
};
