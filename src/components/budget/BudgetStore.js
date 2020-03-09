
export default {
  account: null,        // One of {null, <account>}
  accounts: {},         // List of accounts [{id, name, fid, type, balance, balancedt, payee, url}, ...]
  categories: {},       // List of categories [{id, name, budget, sortindex, comment, url}, ...]
  demo: false,          // Set true to hide sensative values
  view: 'month',        // One of {budget, transactions}
  // Cell Selection
  cursor: null,         // Current cell hovered on
  selected: [],         // Currently selected cells
  editing: false,       // Set True when editing
};
