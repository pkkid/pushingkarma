<template>
  <transition name='fadeslow'>
    <div id='dropzone' v-if='showOverlay'>
      <div class='outline' >drop .qfx</div>
    </div>
  </transition>
</template>

<script>
  import {forEach} from 'lodash';
  import {axios, makeRequest} from '@/utils/utils';
  var API_UPLOAD = '/api/transactions/upload';

  export default {
    name: 'BudgetAccounts',
    data: () => ({
      first: false,
      second: false,
      showOverlay: false,
    }),

    // Created / Destroyed
    // Bind and unbind the drag events when component active
    created: function() {
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
        if (this.first) { this.second = true; }
        else { this.first = true; }
        this.showOverlay = true;
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
        var formdata = new FormData();
        forEach(event.dataTransfer.files, function(file) {
          formdata.append(file.name, file);
        });
        var request = makeRequest(axios.put, API_UPLOAD, formdata);
        request.xhr.then(function(response) {
          console.log(response);
        });
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
    .outline {
      border-radius: 20px;
      border: 5px dashed #89826F;
      font-size: 120px;
      margin: 50px 100px;
      padding: 50px;
      text-align: center;
    }
  }
</style>
