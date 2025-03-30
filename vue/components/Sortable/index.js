export {default as Sortable} from './Sortable.vue'
export {default as SortableItem} from './SortableItem.vue'

// Sortable State
// Global sortable state, this works because there can
// only be one item being dragged at a time.
export var sortableState = {group:null, itemid:null}
