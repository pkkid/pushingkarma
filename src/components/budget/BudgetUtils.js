import {TYPES} from '@/components/TableMixin';

// Default Categories often found useful when building table structures
export var UNCATEGORIZED = {name:'Uncategorized', budget:0};
export var TOTAL = {name:'Total', budget:0, meta:{type:TYPES.readonly, cls:'totalrow'}};
