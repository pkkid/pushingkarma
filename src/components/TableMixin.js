// TableMixin.js
// Vue Mixin that works with a Buefy table to provide keyboard navigation and
// editing ability. Instructions for using this are outlined below:
//
// 1. Import TableMixin object and add it to the mixins: [TableMixin]
// 2. Create columns data variable containins a list of dicts for each column:
//      Column options include the following:
//       * name: Required column name used in the header.
//       * field: Required column field to lookup the value.
//       * editable: Optionally set true if this column is editable.
//       * select: Optionally set true to select all text when beginning edit.
//       * display: Optionally pass function to modify display string.
//      data: () => ({
//        columns: [
//          {name:'Name', field:'name', editable:true},
//          {name:'FID', field:'fid', editable:true, select:true},
//          {name:'Balance', field:'balance', display:utils.usd},
//      ]}),
// 3. Create an 'items' variable in the component containins a list of dicts for each row.
// 4. Create 'keymap' entry in computed variable with at least thee following..
//      keymap: function() { return this.tablemixin_keymap(); },
// 5. Create save() method that will be called when a cell needs to be saved.
// 6. Create the table object in the componet:
//      <b-table :data='tabledata' :narrowed='true' :hoverable='true' v-click-outside='cancelAll'>
//        <template slot-scope='props'>
//          <b-table-column v-for='data in props.row' :key='props.index+data.field' :label='data.name'>
//            <TableCell v-bind='{data, focus, editing}' @click.native='clickSetFocus($event, data.tabindex)'/>
//          </b-table-column>
//        </template>
//        <template slot='empty'>No items to display.</template>
//      </b-table>
//
import TableCell from '@/components/TableCell';

export default {
  components: {TableCell},
  data: () => ({
    focus: null,                // Current focused cell number
    editing: false,             // True if editing
    sortfield: null,            // Specify sortfield to allow reordering
  }),
  computed: {
    items: function() { return []; },  // Required to be populated by parent Compoennt
    cell: function() { return this.getCell(this.focus); },
    editcols: function() { return this.columns.filter(c => c.editable).length; }, 
    maxfocus: function() { return this.items ? this.items.length * this.editcols : 0; },
    
    // Table cells
    // Mold the data rows into a list of lists of cells
    tabledata: function() {
      var rows = [];
      for (var i in this.items) {
        var row=[], editcount=0;
        for (var col of this.columns) {
          editcount += col.editable ? 1 : 0;
          var tabindex = col.editable ? (i * this.editcols) + editcount : null;
          var cell = Object.assign({}, col, {
            row: i,                             // Item row index
            id: this.items[i].id || null,       // Item ID (from the db)
            value: this.items[i][col.field],    // Cell value items[row][field]
            tabindex: tabindex,                 // Cell tabindex for keyboard nav
            width: col.width || null,           // Cell width
          });
          row.push(cell);
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
        'up': (event) => this.navigate(event, -this.editcols),
        'down': (event) => this.navigate(event, this.editcols),
        'left': (event) => this.navigate(event, -1),
        'right': (event) => this.navigate(event, 1),
        'tab': (event) => this.navigate(event, 1, true, true),
        'shift+tab': (event) => this.navigate(event, -1, true, true),
        'shift+up': (event) => this.reorder(event, -1),
        'shift+down': (event) => this.reorder(event, 1),
        'space': (event) => this.toggleValue(event),
        'enter': (event) => this.enterEditOrSave(event),
        'esc': (event) => this.cancelEdit(event),
      };
    },

    // Add
    // Add new row to populate, not yet saved to the db.
    // Generic helper function to add a new row.
    add: function() {
      this.items.push({});
      this.setFocusLast();
    },

    // Cancel All
    // Called when user clicks off the table
    cancelAll: function() {
      if (this.focus || this.editing) {
        this.editing = false;
        this.focus = null;
      }
    },

    // Cancel Edit
    // Called when user hits esc
    cancelEdit: function(event) {
      if (!this.inContainer()) { return; }
      if (this.cell.id == null && this.cell.newvalue == '') {
        // Cancel editing & refresh
        event.preventDefault();
        document.getSelection().removeAllRanges();
        this.editing = false;
        this.focus = null;
        this.refresh();
      } else if (this.editing) {
        // Cancel editing
        event.preventDefault();
        document.getSelection().removeAllRanges();
        this.getCell().$el.focus();
        this.editing = false;
      } else if (this.focus) {
        // Clear focus
        event.preventDefault();
        this.focus = null;
      }
    },

    // Enter: Edit or Save
    // Called when user hits enter on the page
    enterEditOrSave: function(event) {
      if (!this.inContainer()) { return; }
      if (this.focus) {
        event.preventDefault();
        var cell = this.getCell();
        if (!this.editing && cell.editable) {
          // Start editing
          this.editing = true;
        } else {
          // Save and goto next item
          this.navigate(event, this.editcols, true, true);
        }
      }
    },

    // Click: Set Focus
    // Called when user clicks on an editable cell
    clickSetFocus: function(event, tabindex) {
      if (tabindex != null) {
        event.preventDefault();
        var cell = this.getCell();
        if (tabindex != this.focus) {
          // Set new focus
          this.focus = tabindex;
          this.editing = false;
        } else if (!cell.editable) {
          // Toggle boolean value
          var newvalue = !cell.data.value;
          this.save(cell, cell.id, cell.row, cell.field, newvalue);
        } else if (!this.editing) {
          // Start editing
          this.editing = true;
        }
      }
    },

    // Get Cell
    // Return cell coresponding to specified tabindex
    getCell: function(tabindex) {
      tabindex = tabindex || this.focus;
      var ref = this.$refs[`c${tabindex}`];
      return ref ? ref[0] : null;
    },

    // Get Row Values
    // Return the full row dataset for the specified cell
    getRowData: function(cell) {
      for (var rowdata of this.items) {
        if (cell.id == rowdata.id) { return rowdata; }
      }
    },

    // In Container
    // Check the document.activeElement is within this container
    inContainer: function() {
      return this.$el.contains(document.activeElement);
    },

    // Navigate
    // Move the focused cell by the amount specified
    navigate: function(event, amount, saveFirst=false, allowEditing=false) {
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (!allowEditing && this.editing) { return; }  // Skip if editing
      event.preventDefault();
      // Save the new value
      var cell = this.getCell();
      if (this.editing && saveFirst) {
        var newvalue = cell.getNewValue();
        if (cell.displayValue != newvalue) {
          this.save(cell, cell.id, cell.row, cell.field, newvalue);
        }
      }
      // Set the new focus
      var newfocus = this.focus + amount;
      if ((newfocus > 0) && (newfocus <= this.maxfocus)) {
        // Navigate to new item
        var newcell = this.getCell(newfocus);
        document.getSelection().removeAllRanges();
        this.editing = newcell.editable ? this.editing : false;
        this.focus = newfocus;
      } else {
        // Reached the end of the table, just stop editing.
        this.editing = false;
      }
    },

    // Reorder
    // Move a table row up or down by the specified amount
    reorder: async function(event, amount) {
      if (!this.sortfield) { return; }  // Skip if sortfield is not specified
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (this.editing) { return; }  // Skip if editing
      event.preventDefault();
      var cell = this.getCell();
      var newrow = parseInt(cell.row) + amount;
      var data = await this.save(null, cell.id, cell.row, this.sortfield, newrow, true);
      this.focus = (data.sortindex * this.editcols) + 1;
    },

    // Set Focus Last
    // Set focus to the first cell in the last row
    setFocusLast: async function() {
      await this.$nextTick();
      this.focus = (this.items.length - 1) * this.editcols + 1;
      this.editing = true;
    },

    // Toggle Value
    // Only for non-editable cells, till toggle current value
    toggleValue: function(event) {
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (this.editing) { return; }  // Skip if editing
      event.preventDefault();
      var cell = this.getCell();
      if (!cell.editable) {
        var newvalue = !cell.data.value;
        this.save(cell, cell.id, cell.row, cell.field, newvalue);
      }
    },

  },
};
