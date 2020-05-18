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
    sortfield: null,      // Specify sortfield to allow reordering
    maxfocus: 0,          // Max tabindex we can focus on
  }),
  computed: {
    items: function() { return []; },  // Required by parent compoennt
    focuscols: function() { return this.columns.filter(c => c.type.focusable).length; },  // Num editcolumns defined
    
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
        this.maxfocus = gtabindex;
        data.push(row);
      }
      return data;
    },
  },
  watch: {
    // Watch Focus
    // Update the required TableCells with the new value
    focus: function(newvalue, oldvalue) {
      var newcell = this.getCell(newvalue);
      var oldcell = this.getCell(oldvalue);
      var editing = oldcell.editing;
      var popped = oldcell.popped;
      document.getSelection().removeAllRanges();
      if (oldvalue) {
        oldcell.focused = false;
        oldcell.editing = false;
        oldcell.popped = false;
      }
      if (newvalue) {
        newcell.focused = true;
        newcell.editing = editing;
        newcell.popped = popped;
        newcell.focus();
      }
    },
  },
  methods: {
    // Get Cell
    // Return cell coresponding to specified tabindex
    getCell: function(tabindex) {
      tabindex = tabindex || this.focus;
      var ref = this.$refs[`c${tabindex}`];
      return ref ? ref[0] : {};
    },

    // In Container
    // Check the document.activeElement is within this container
    inContainer: function() {
      return this.$refs.table.$el.contains(document.activeElement);
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
    add: async function() {
      this.items.push({});
      // set focus to last new item
      await this.$nextTick();
      this.focus = (this.items.length-1) * this.focuscols+1;
      this.getCell().editing = true;
    },

    // Cancel Edit
    // Called when user hits esc
    cancel: function(event) {
      var cell = this.getCell();
      var item = cell.row;
      if (!this.inContainer()) { return; }
      if (cell.popped) {
        // hide popover
        event.preventDefault();
        cell.popped = false;
      } else if (cell.editing && (item.id == null)) {
        // cancel new item
        event.preventDefault();
        document.getSelection().removeAllRanges();
        cell.editing = false;
        this.focus = null;
        this.refresh();
      } else if (cell.editing) {
        // cancel editing
        event.preventDefault();
        document.getSelection().removeAllRanges();
        cell.$el.focus();
        cell.editing = false;
      } else if (this.focus) {
        // clear focus
        event.preventDefault();
        this.focus = null;
      }
    },

    // Cancel All
    // Called when user clicks off the table
    cancelAll: function() {
      var cell = this.getCell();
      if (this.focus || cell.editing) {
        cell.editing = false;
        cell.popped = false;
        this.focus = null;
      }
    },

    // Click: Set Focus
    // Called when user clicks on an editable cell
    click: function(event, tabindex) {
      if (tabindex != null) {
        var cell = this.getCell(tabindex);
        if (cell.focusable && (tabindex != this.focus)) {
          // focus on cell
          event.preventDefault();
          this.focus = tabindex;
          cell.editing = false;
        } else if (cell.toggleable) {
          // toggle value
          event.preventDefault();
          var newvalue = !cell.value;
          this.save(cell.item.id, cell.col.field, newvalue, cell);
        } else if (cell.poppable && !cell.popped) {
          // show popover
          event.preventDefault();
          cell.popped = true;
        } else if (cell.editable && !cell.editing) {
          // start editing
          event.preventDefault();
          cell.editing = true;
        }
      }
    },

    // Enter: Edit or Save
    // Called when user hits enter on the page
    enter: function(event) {
      if (!this.inContainer()) { return; }
      if (this.focus) {
        var cell = this.getCell();
        if (cell.toggleable) {
          // toggle value
          event.preventDefault();
          this.toggle(event);
          this.navigate(event, this.focuscols, true, true);
        } else if (cell.poppable) {
          // show popover
          event.preventDefault();
          cell.popped = true;
        } else if (cell.editable && !cell.editing) {
          // start editing
          event.preventDefault();
          cell.editing = true;
        } else if (cell.editable && cell.editing) {
          // save and navigate
          event.preventDefault();
          this.navigate(event, this.focuscols, true, true);
        }
      }
    },

    // Navigate
    // Move the focused cell by the amount specified
    navigate: async function(event, amount, saveFirst=false, allowEditing=false) {
      var cell = this.getCell();
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (!allowEditing && cell.editing) { return; }  // Skip if editing
      event.preventDefault();
      // Save the new value
      if (cell.editing && saveFirst) {
        var oldvalue = utils.textContent(cell.html);
        var newvalue = cell.text;
        if (oldvalue != newvalue) {
          console.log(`Saving ${cell.col.field}: '${oldvalue}' != '${newvalue}'`);
          this.save(cell.item.id, cell.col.field, newvalue, cell);
        }
      }
      // Set the new focus
      var newfocus = this.focus + amount;
      if ((newfocus > 0) && (newfocus <= this.maxfocus)) {
        // navigate to new item
        this.focus = newfocus;
      } else {
        // reached the end of the table, just stop editing.
        cell.editing = false;
      }
    },

    // Reorder
    // Move a table row up or down by the specified amount
    reorder: async function(event, amount) {
      var cell = this.getCell();
      if (!this.sortfield) { return; }  // Skip if sortfield is not specified
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (cell.editing) { return; }  // Skip if editing
      event.preventDefault();
      var newrow = parseInt(cell.rowindex) + amount;
      var data = await this.save(cell.item.id, this.sortfield, newrow, null, true);
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
        this.save(cell.item.id, cell.col.field, '_RESET', cell);
      }
    },

    // Toggle Value
    // Only for non-editable cells, till toggle current value
    toggle: function(event) {
      var cell = this.getCell();
      if (!this.inContainer()) { return; }  // Skip if not in container
      if (!this.focus) { return; }  // Skip if nothing selected
      if (cell.editing) { return; }  // Skip if editing
      event.preventDefault();
      if (!cell.editable) {
        var newvalue = !cell.value;
        this.save(cell.item.id, cell.col.field, newvalue, cell);
      }
    },

    // Update Item
    // Set new value for the specified item ID
    updateItem: function(id, data) {
      for (var i in this.items) {
        if (this.items[i].id == id) {
          this.$set(this.items, i, data);
          break;
        }
      }
    },

  },
};
