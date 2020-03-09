<template>
  <transition name='custom-classes-transition'
      enter-active-class='animated fadeIn'
      leave-active-class='animated fadeOut'>
    <div id='dropzone' v-if='showOverlay'>
      <div class='outline' >drop .qfx</div>
    </div>
  </transition>
</template>

<script>
  export default {
    name: 'Dropzone',
    data: () => ({
      first: false,
      second: false,
      showOverlay: false,
    }),

    // Created / Destroyed
    // Bind and unbind the drag events when component active
    mounted: function() {
      document.addEventListener('dragover', this.dragEnter);
      document.addEventListener('dragleave', this.dragLeave);
      document.addEventListener('drop', this.dropFile);
    },
    destroyed: function() {
      document.removeEventListener('dragover', this.dragEnter);
      document.removeEventListener('dragleave', this.dragLeave);
      document.removeEventListener('drop', this.dropFile);
    },

    methods: {
      // Drag Enter / Drag Leave
      // Triggered when we drag a file into or out of the window
      // https://github.com/bensmithett/dragster/blob/gh-pages/src/dragster.coffee
      dragEnter: function(event) {
        event.preventDefault();
        event.stopPropagation();
        if (event.dataTransfer.types.indexOf('Files') != -1) {
          if (this.first) { this.second = true; }
          else { this.first = true; }
          this.showOverlay = true;
        }
      },
      dragLeave: function(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.second) { this.second = false; }
        else if (this.first) { this.first = false; }
        if (!this.first && !this.second) {
          this.showOverlay = false;
        }
      },

      // Drop File
      // Triggered when we drop
      dropFile: function(event) {
        event.preventDefault();
        event.stopPropagation();
        this.showOverlay = false;
        var files = event.dataTransfer.files;
        var formdata = new FormData();
        for (var i=0; i<event.dataTransfer.files.length; i++) {
          console.log(files[i].name +"; "+ files[i]);
          formdata.append(files[i].name, files[i]);
        }
        this.$emit('filesDropped', formdata);
      },
    }
  };
</script>

<style lang='scss'>
  #dropzone {
    border: 1px solid red;
    height: 100%;
    left: 0;
    position: absolute;
    top: 0;
    width: 100%;
    z-index: 90;
    background-color: rgba(255,255,255,0.8);
    .outline {
      border-radius: 20px;
      border: 5px dashed #89826F;
      font-size: 7.5rem;
      margin: 50px 100px;
      padding: 50px;
      text-align: center;
    }
  }
</style>
