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
//            <TableCell v-bind='{data, focus, editing}' @click.native='click($event, data.tabindex)'/>
//          </b-table-column>
//        </template>
//        <template slot='empty'>No items to display.</template>
//      </b-table>
import * as utils from '@/utils/utils';
import TableCell from '@/components/TableCell';
import trim from 'lodash/trim';

export const TYPES = {
  readonly: {name:'readonly', focusable:false, editable:false},
  editable: {name:'editable', focusable:true, editable:true},
  toggle: {name:'toggle', focusable:true, editable:false},
  choice: {name:'choice', focusable:true, editable:true, requires:['choices']},
  popover: {name:'popover', focusable:true, editable:false, requires:['content']},
};

export default {
  components: {TableCell},
  data: () => ({
    focus: null,          // Current focused cell number
    editing: false,       // True if editing
    sortfield: null,      // Specify sortfield to allow reordering
  }),
  computed: {
    items: function() { return []; },                                                      // Required by parent compoennt
    item: function() { return this.getCell(this.focus).row; },                             // Current focused cell data
    focuscols: function() { return this.columns.filter(c => c.type.focusable).length; },   // Count of editcolumns defined
    maxfocus: function() { return this.items ? this.items.length * this.focuscols : 0; },  // Max tabindex we can focus on
    
    // Table cells
    // Mold the data rows into a list of lists of cells
    tabledata: function() {
      var data = [];                  // Data passed to Buefy table
      var gtabindex = 0;              // Global tabindex
      for (var i in this.items) {
        var row = [];                 // List of cell objects
        for (var col of this.columns) {
          col.type = col.type || TYPES.readonly;
          col['header-class'] = trim(`${col.cls || ''} ${col.type.name}`);
          col['cell-class'] = trim(`${col.cls || ''} ${col.type.name}`);
          gtabindex += col.type.focusable ? 1 : 0;
          var tabindex = col.type.focusable ? gtabindex : null;
          var cell = Object.assign({}, {
            col: col,                 // Column data for this cell
            row: this.items[i],       // Row data for this cell
            rowindex: parseInt(i),    // Current display row index
            tabindex: tabindex,       // Cell tabindex for keyboard nav (null if not focusable)
          });
          row.push(cell);
        }
        data.push(row);
      }
      return data;
    },
  },
  watch: {
    // Watch Focus
    // Update the required TableCells with the new value
    focus: function(newvalue, oldvalue) {
      if (oldvalue) {
        var oldcell = this.getCell(oldvalue);
        oldcell.focused = false;
        oldcell.editing = false;
      }
      if (newvalue) {
        var newcell = this.getCell(newvalue);
        newcell.focused = true;
        newcell.editing = this.editing;
      }
    },
    // Watch Editing
    // Update the required TableCells with the new value
    editing: function(newvalue) {
      var cell = this.getCell();
      if (cell !== null) { cell.editing = newvalue; }
    }
  },
  methods: {
    // Get Cell
    // Return cell coresponding to specified tabindex
    getCell: function(tabindex) {
      tabindex = tabindex || this.focus;
      var ref = this.$refs[`c${tabindex}`];
      return ref ? ref[0] : null;
    },

    // In Container
    // Check the document.activeElement is within this container
    inContainer: function() {
      return this.$refs.table.$el.contains(document.activeElement);
    },

    // Set Focus Last
    // Set focus to the first cell in the last row
    setFocusLast: async function() {
      await this.$nextTick();
      this.focus = (this.items.length - 1) * this.focuscols + 1;
      this.editing = true;
    },
    
    // TableMixin Keymap
    // Keymaps used with this mixin.
    tableMixinKeymap: function() {
      return {
        'up': (event) => this.navigate(event, -this.focuscols),
        'down': (event) => this.navigate(event, this.focuscols),
        'left': (event) => this.navigate(event, -1),
        'right': (event) => this.navigate(event, 1),
        'tab': (event) => this.navigate(event, 1, true, true),
        'shift+tab': (event) => this.navigate(event, -1, true, true),
        'shift+up': (event) => this.reorder(event, -1),
        'shift+down': (event) => this.reorder(event, 1),
        'space': (event) => this.toggle(event),
        'enter': (event) => this.enter(event),
        'ctrl+z': (event) => this.resetValue(event),
        'esc': (event) => this.cancel(event),
      };
    },

    // Add
    // Add new row to populate, not yet saved to the db.
    // Generic helper function to add a new row.
    add: function() {
      this.items.push({});
      this.setFocusLast();
    },

    // Cancel Edit
    // Called when user hits esc
    cancel: function(event) {
      if (!this.inContainer()) { return; }
      if (this.item.id == null) {
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

    // Cancel All
    // Called when user clicks off the table
    cancelAll: function() {
      if (this.focus || this.editing) {
        this.editing = false;
        this.focus = null;
      }
    },

    // Click: Set Focus
    // Called when user clicks on an editable cell
    click: function(event, tabindex) {
      if (tabindex != null) {
        event.preventDefault();
        var cell = this.getCell();
        if (tabindex != this.focus) {
          // Set new focus
          this.focus = tabindex;
          this.editing = false;
        } else if (!cell.editable) {
          // Toggle boolean value
          var newvalue = !cell.value;
          this.save(cell.item.id, cell.rowindex, cell.col.field, newvalue, cell);
        } else if (!this.editing) {
          // Start editing
          this.editing = true;
        }
      }
    },

    // Enter: Edit or Save
    // Called when user hits enter on the page
    enter: function(event) {
      if (!this.inContainer()) { return; }
      if (this.focus) {
        event.preventDefault();
        var cell = this.getCell();
        if (!this.editing && cell.editable) {
          // Start editing
          this.editing = true;
        } else {
          // Save and goto next item
          if (!cell.editable) { this.toggle(event); }
          this.navigate(event, this.focuscols, true, true);
        }
      }
    },

    // Navigate
    // Move the focused cell by the amount specified
    navigate: function(event, amount, saveFirst=false, allowEditing=false) {
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (!allowEditing && this.editing) { return; }  // Skip if editing
      event.preventDefault();
      // Save the new value
      if (this.editing && saveFirst) {
        var cell = this.getCell();
        var oldvalue = utils.textContent(cell.html);
        var newvalue = cell.text;
        if (oldvalue != newvalue) {
          console.log(`Saving ${cell.col.field}: '${oldvalue}' != '${newvalue}'`);
          this.save(cell.item.id, cell.rowindex, cell.col.field, newvalue, cell);
        } else {
          cell.setStatus('default');
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
      var newrow = parseInt(cell.rowindex) + amount;
      var data = await this.save(cell.item.id, cell.rowindex, this.sortfield, newrow, null, true);
      this.focus = (data.sortindex * this.focuscols) + 1;
    },

    // Enter: Edit or Save
    // Called when user hits enter on the page
    resetValue: function(event) {
      if (!this.inContainer()) { return; }
      if (this.focus) {
        var cell = this.getCell();
        if (!cell.col.reset) { return; }
        event.preventDefault();
        this.save(cell.item.id, cell.rowindex, cell.col.field, '_RESET', cell);
      }
    },

    // Toggle Value
    // Only for non-editable cells, till toggle current value
    toggle: function(event) {
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (this.editing) { return; }  // Skip if editing
      event.preventDefault();
      var cell = this.getCell();
      if (!cell.editable) {
        var newvalue = !cell.value;
        this.save(cell.item.id, cell.rowindex, cell.col.field, newvalue, cell);
      }
    },

  },
};
