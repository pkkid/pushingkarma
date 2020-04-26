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
    focus: null,      // Current focused cell number
    editing: false,   // True if editing
  }),
  computed: {
    items: function() { return []; },
    editcolumns: function() { return this.columns.filter(c => c.editable).length; }, 
    maxfocus: function() { return this.items ? this.items.length * this.editcolumns : 0; },
    
    // Table cells
    // Mold the data rows into a list of lists of cells
    tabledata: function() {
      var rows = [];
      for (var i in this.items) {
        var row = [];
        var roweditcount = 0;
        for (var column of this.columns) {
          var data = Object.assign({}, column);
          roweditcount += data.editable ? 1 : 0;
          data.row = i;
          data.id = this.items[i].id;
          data.value = this.items[i][data.field];
          data.tabindex = data.editable ? (i*this.editcolumns)+roweditcount : null;
          data.width = column.width || null;
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
    clickSetFocus: function(event, tabindex) {
      if (tabindex != null) {
        event.preventDefault();
        if (tabindex != this.focus) {
          // Set new focus
          this.focus = tabindex;
          this.editing = false;
        } else if (!this.editing) {
          // Start editing
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
          // Start editing
          this.editing = true;
        } else {
          // Save and goto next item
          this.save(event, this.focus);
          this.navigate(event, this.editcolumns, true);
        }
      }
    },

    // Cancel Edit
    // Called when user hits esc
    cancelEdit: function(event) {
      if (this.editing) {
        // Cancel editing
        event.preventDefault();
        document.getSelection().removeAllRanges();
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
        // Cancel all
        this.editing = false;
        this.focus = null;
      }
    },

    // Navigate
    // Move the focused cell by the amount specified
    navigate: function(event, amount, allowEditing=false) {
      if (!this.focus) { return; }
      if (!allowEditing && this.editing) { return; }
      event.preventDefault();
      var newfocus = this.focus + amount;
      if ((newfocus > 0) && (newfocus <= this.maxfocus)) {
        // Navigate to new item
        this.focus = newfocus;
      }
    },

  },
};
