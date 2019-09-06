<template>
  <div id="swatchColors">
    <div class="colorSwatch" :style="{'width':size+'px', 'height':size+'px', 'background-color':color, 'border-radius':round ? '25%':'0%' }" 
        v-for="color in rgba ? rgbaColors : colors" :key="color"
        @click="$emit('input', color)" >
      <q-icon class="transpColorIcon" v-if="color === 'transparent'" name="clear" />
      <q-icon v-if="color === value" class="transpColorIcon" :color="colorBorW(color)" name="check"/>
      <q-tooltip>{{color}}</q-tooltip>
    </div>
  </div>
</template>

<script>
  export default {
    props: { 
      size: {required: false, type: Number, default: 24 },
      round: {required: false, type: Boolean, default: true },
      inPopover: {require: false, type: Boolean, default: false },
      value: {required: false, type: String, default: '#ffffff'},
      rgba: {required: false, type: Boolean, default: false}
    },
    data() {
      return { 
        colors: [ '#ffffff', '#000000', '#ef5350', '#ff1744', '#f06292', '#ce93d8', '#6a1b9a', '#d500f9', '#311b92',
          '#651fff', '#7986cb', '#536dfe', '#4fc3f7', '#00acc1', '#006064', '#009688', '#66bb6a', '#2e7d32', '#64dd17',
          '#aed581', '#afb42b', '#aeea00', '#fdd835', '#f57f17', '#ffb300', '#ff6f00', '#fb8c00', '#e65100', '#bf360c',
          '#ff3d00', '#bcaaa4', '#5d4037', '#9e9e9e', '#616161', '#90a4ae', '#546e7a', 'transparent'
        ],
        rgbaColors: ['rgba(255, 255, 255, 1)', 'rgba(0, 0, 0, 1)', 'rgba(239, 83, 80, 1)', 'rgba(255, 23, 68, 1)', 'rgba(240, 98, 146, 1)',
          'rgba(206, 147, 216, 1)', 'rgba(106, 27, 154, 1)', 'rgba(213, 0, 249, 1)', 'rgba(49, 27, 146, 1)', 'rgba(101, 31, 255, 1)',
          'rgba(121, 134, 203, 1)', 'rgba(83, 109, 254, 1)', 'rgba(79, 195, 247, 1)', 'rgba(0, 172, 193, 1)', 'rgba(0, 96, 100, 1)',
          'rgba(0, 150, 136, 1)', 'rgba(102, 187, 106, 1)', 'rgba(46, 125, 50, 1)', 'rgba(100, 221, 23, 1)', 'rgba(174, 213, 129, 1)',
          'rgba(175, 180, 43, 1)', 'rgba(174, 234, 0, 1)', 'rgba(253, 216, 53, 1)', 'rgba(245, 127, 23, 1)', 'rgba(255, 179, 0, 1)',
          'rgba(255, 111, 0, 1)', 'rgba(251, 140, 0, 1)', 'rgba(230, 81, 0, 1)', 'rgba(191, 54, 12, 1)', 'rgba(255, 61, 0, 1)',
          'rgba(188, 170, 164, 1)', 'rgba(93, 64, 55, 1)', 'rgba(158, 158, 158, 1)', 'rgba(97, 97, 97, 1)', 'rgba(144, 164, 174, 1)',
          'rgba(84, 110, 122, 1)', 'rgba(0, 0, 0, 0)'
        ]
      };
    },
    methods: {
      // Helps to create high contrast text over color, it answers if the color
      // you give is dark or white in order to show the opposite text over it.
      colorBorW(color) {
        if(color === 'transparent') color = "#ffffff";
        var c = color.substring(1);  // strip #
        var rgb = parseInt(c, 16);   // convert rrggbb to decimal
        var r = (rgb >> 16) & 0xff;  // extract red
        var g = (rgb >>  8) & 0xff;  // extract green
        var b = (rgb >>  0) & 0xff;  // extract blue
        var luma = 0.2126 * r + 0.7152 * g + 0.0722 * b; // per ITU-R BT.709
        if (luma > 150) return 'black';
        else return 'white';
      }
    }
  };
</script>

<style scoped>
  #swatchColors {
    width:25rem;
  }
  .transpColorIcon {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
  }
  .colorSwatch {
      display: -webkit-inline-flex;
      position: relative;
      margin: 2px;
      border-style: dashed;
      border-width: 1px;
      border-color: blueviolet;
      cursor: pointer;
  }
</style>
