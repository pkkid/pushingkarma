<template>
  <div id='dropzone' @dragover='dragover' @dragleave='dragleave' @drop='drop'>
    <transition name='custom-classes-transition' enter-active-class='animated fadeIn' leave-active-class='animated fadeOut'>
      <div id='dropoverlay' v-if='show'>
        <div class='outline' >drop .qfx</div>
      </div>
    </transition>
    <slot/>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';

  export default {
    name: 'Dropzone',
    data: () => ({
      show: false,
      timer: null,
    }),
    methods: {
      dragover: function(event) {
        if (utils.dragType(event) != 'file') { return; }
        event.preventDefault();
        window.clearTimeout(this.timer);
        this.show = true;
      },
      dragleave: function(event) {
        if (utils.dragType(event) != 'file') { return; }
        event.preventDefault();
        this.timer = window.setTimeout(() => this.show = false, 500);
      },
      drop: function(event) {
        if (utils.dragType(event) != 'file') { return; }
        event.preventDefault();
        event.stopPropagation();
        this.show = false;
        var files = event.dataTransfer.files;
        var formdata = new FormData();
        for (var i=0; i<event.dataTransfer.files.length; i++) {
          console.log(`Dropped ${files[i].name}`);
          formdata.append(files[i].name, files[i]);
        }
        this.$emit('filesDropped', formdata);
      },
    }
  };
</script>

<style lang='scss'>
  #dropzone {
    position: relative;
  }
  #dropoverlay {
    background-color: rgba($lightbg-bg2, 0.9);
    height: 100%;
    left: 0px;
    position: absolute;
    top: 0px;
    width: 100%;
    z-index: 28;
    * { pointer-events: none; }
    .outline {
      border-radius: 20px;
      border: 5px dashed $lightbg-fg4;
      color: $lightbg-fg3;
      font-family: $fontfamily-title;
      font-size: 7.5rem;
      top: 130px;
      right: calc(50% - 550px);
      padding: 50px;
      position: fixed;
      text-align: center;
      width: 800px;
    }
  }
</style>
