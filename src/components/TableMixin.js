import map from 'lodash/map';
import TableCell from '@/components/TableCell';

export default {
  components: {TableCell},
  data: () => ({
    focus: null,      // Current focused cell number
    editing: false,   // True if editing
  }),
  computed: {
    items: function() { return []; },
    editcolumns: function() { return Math.max(...map(this.columns, (column) => column.id || 0)); }, 
    maxfocus: function() { return this.items ? this.items.length * this.editcolumns : 0; },
    
    // Table cells
    // Mold the data rows into a list of lists of cells
    tabledata: function() {
      var rows = [];
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
    // TableMixin Keymap
    // Keymaps used with this mixin.
    tablemixin_keymap: function() {
      return {
        'up': (event) => this.navigate(event, -this.editcolumns),
        'down': (event) => this.navigate(event, this.editcolumns),
        'left': (event) => this.navigate(event, -1),
        'right': (event) => this.navigate(event, 1),
        'tab': (event) => this.navigate(event, 1),
        'shift+tab': (event) => this.navigate(event, -1),
        'enter': (event) => this.enterEditOrSave(event),
        'esc': (event) => this.cancelEdit(event),
      };
    },

    // Click: Set Focus
    // Called when user clicks on an editable cell
    clickSetFocus: function(event, gid) {
      if (gid != null) {
        event.preventDefault();
        if (gid != this.focus) {
          console.log(`Set new focus: ${gid}`);
          this.focus = gid;
          this.editing = false;
        } else if (!this.editing) {
          console.log(`Start editing ${this.focus}`);
          this.editing = true;
        }
      }
    },

    // Enter: Edit or Save
    // Called when user hits enter on the page
    enterEditOrSave: function(event) {
      if (this.focus) {
        event.preventDefault();
        if (!this.editing) {
          console.log(`Start editing ${this.focus}`);
          this.editing = true;
        } else {
          console.log(`Save value..`);
          this.navigate(event, this.editcolumns);
        }
      }
    },

    // Cancel Edit
    // Called when user hits esc
    cancelEdit: function(event) {
      if (this.editing) {
        event.preventDefault();
        console.log(`Cancel editing ${this.focus}`);
        this.editing = false;
      } else if (this.focus) {
        event.preventDefault();
        console.log(`Clear focus`);
        this.focus = null;
      }
    },

    // Cancel All
    // Called when user clicks off the table
    cancelAll: function() {
      if (this.focus || this.editing) {
        console.log(`Cancel all`);
        this.editing = false;
        this.focus = null;
      }
    },

    // Navigate
    // Move the focused cell by the amount specified
    navigate: function(event, amount) {
      if (!this.focus) { return; }
      if (this.editing) { return; }
      event.preventDefault();
      var newfocus = this.focus + amount;
      if ((newfocus > 0) && (newfocus <= this.maxfocus)) {
        console.log(`Navigate to ${newfocus}`);
        this.focus = newfocus;
      }
    },

  },
};
