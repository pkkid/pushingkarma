<template>
  <div id='dropzone' @dragover='onDragover' @dragleave='onDragleave' @drop='onDrop'>
    <Transition name='fade'>
      <div id='dropoverlay' v-if='show'>
        <div class='outline' >
          <div>{{text}}</div>
          <div v-if='subtext' class='subtext'>{{subtext}}</div>
          <span :class='icon'/>
        </div>
      </div>
    </Transition>
    <slot></slot>
  </div>
</template>

<script setup>
  import {ref} from 'vue'
  
  var timer = null
  const props = defineProps({
    text: {default:'Drop Files'},
    subtext: {default:null},
    icon: {default:'mdi mdi-file-upload-outline'},
  })
  const emit = defineEmits(['filesDropped'])
  const show = ref(false)

  // On Drag Over
  // Display the overlay
  const onDragover = function(event) {
    if (dragType(event) != 'file') { return }
    event.preventDefault()
    window.clearTimeout(timer)
    show.value = true
  }

  // On Drag Leave
  // Start the timer to hide the overlay
  const onDragleave = function(event) {
    if (dragType(event) != 'file') { return }
    event.preventDefault()
    timer = window.setTimeout(() => show.value = false, 500)
  }

  // On Drop
  // Emit event that we dropped a file
  const onDrop = function(event) {
    if (dragType(event) != 'file') { return }
    event.preventDefault()
    event.stopPropagation()
    show.value = false
    var files = event.dataTransfer.files
    var formdata = new FormData()
    for (var i=0; i<event.dataTransfer.files.length; i++) {
      console.log(`Dropped ${files[i].name}`)
      formdata.append('files', files[i])
    }
    emit('filesDropped', event, formdata)
  }

  // Drag Type
  // Returns the type of drag event
  const dragType = function(event) {
    if (!event.dataTransfer) { return }
    var dt = event.dataTransfer
    var hasFiles = dt.types?.indexOf ? dt.types.indexOf('Files') != -1 : dt.types.contains('Files')
    return hasFiles ? 'file' : 'element'
  }
</script>

<style>
  #dropzone {
    position: relative;
    #dropoverlay {
      background-color: var(--lightbg-bg2);
      position: absolute;
      top: 0px; left: 0px;
      width: 100%; height: 100%;
      z-index: 9;
      * { pointer-events: none; }
      .outline {
        border-radius: 20px;
        border: 5px dashed var(--lightbg-fg4);
        color: var(--lightbg-fg3);
        font-family: var(--fontfamily-title);
        font-size: 50px;
        top: 130px;
        right: calc(50% - 550px);
        padding: 50px;
        position: fixed;
        text-align: center;
        width: 800px;
        .subtext { font-size:25px; margin-bottom:10px; }
        .mdi { font-size: 80px; }
      }
    }
  }
</style>
