import * as utils from '@/utils/utils';
import map from 'lodash/map';

export default {
  data: () => ({
    focus: null,      // Current focused cell number
    editing: false,   // True if editing
    utils: utils,
  }),
  computed: {
    items: function() { return []; },
    editcolumns: function() { return Math.max(...map(this.columns, (column) => column.id || 0)); }, 
    maxfocus: function() { return this.items ? this.items.length * this.editcolumns : 0; },
    
    // Table cells
    // Mold the data rows into a list of lists of cells
    tabledata: function() {
      var rows = [];
      console.log(this.editcolumns);
      for (var i in this.items) {
        var row = [];
        for (var column of this.columns) {
          var data = Object.assign({}, column); 
          data.value = this.items[i][data.field];
          data.gid = data.id ? (i*this.editcolumns)+data.id : null;
          row.push(data);
        }
        rows.push(row);
      }
      return rows;
    },

  },
  methods: {
    // Focused Event
    // Called when user clicks on an editable cell
    focusOn: function(event, gid) {
      event.preventDefault();
      if (gid && gid != this.focus) {
        this.focus = gid;
      }
    },

    navigate: function(event, amount) {
      if (this.focus == null) { return; }
      event.preventDefault();
      var newfocus = this.focus + amount;
      if ((newfocus > 0) && (newfocus <= this.maxfocus)) {
        this.focus = newfocus;
      }
    },

  },
};
