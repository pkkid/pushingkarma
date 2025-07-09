<template>
  <div class='gallery' :class='type'>
    <div v-for='photo in photos.items' class='gallery-img vignette' :key='photo.url'>
      <img :src='photo.url'/>
    </div>
  </div>
</template>

<script setup>
  // Implements the Obsidian Image Gallery Plugin for MarkdownIt
  // https://github.com/lucaorio/obsidian-image-gallery
  import {computed, onMounted, ref} from 'vue'
  import {api} from '@/utils'

  const props = defineProps({
    path: {type:String, default:''},              // Path relative to the root of the vault
    type: {type:String, default:'horizontal'},    // Type of masonry (horizontal, vertical)
    gutter: {type:Number, default:8},             // Spacing in px between the images
    radius: {type:Number, default:0},             // Border radius in px of the images
    sortby: {type:String, default:'ctime'},       // Sort images by (ctime,	mtime, name)
    sort: {type:String, default:'desc'},          // Order of sorting (desc, asc)
    height: {type:Number, default:260},           // Horizontal type only; Height in px of all rows
    columns: {type:Number, default:3},            // Vertical type only; Number of columns for desktop
  })
  const loading = ref(false)                      // True to show loading indicator
  const photos = ref([])                          // List of photos to display

  onMounted(function() { updatePhotos() })
  const gutter = computed(() => `${props.gutter}px`)
  const height = computed(() => `${props.height}px`)
  const radius = computed(() => `${props.radius}px`)

  // Update Photos
  // Fetches the list of photos from the Obsidian vault
  const updatePhotos = async function() {
    loading.value = true
    try {
      var bucket, staticpath
      if (props.path.startsWith('PushingKarma')) {
        staticpath = props.path.replace('PushingKarma/_static/', '')
        bucket = 'public'
      } else if (props.path.startsWith('Private')) {
        staticpath = props.path.replace('Private/_static/', '')
        bucket = 'private'
      }
      var params = {sortby:props.sortby, sort:props.sort}
      var {data} = await api.Obsidian.listStatic(bucket, staticpath, params)
      photos.value = data
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }
</script>

<style>
  .gallery {
    /* Vertical Layout */
    &.vertical {
      line-height: 0px;
      column-count: v-bind(columns);
      column-gap: v-bind(gutter);
      .gallery-img {
        border-radius: v-bind(radius);
        height: auto;
        margin-bottom: v-bind(gutter);
        overflow: hidden;
        width: 100%;
      }
    }

    /* Horizontal Layout */
    &.horizontal {
      display: flex;
      flex-wrap: wrap;
      margin-right: v-bind(gutter);

      .gallery-img {
        margin-right: v-bind(gutter);
        margin-bottom: v-bind(gutter);
        width: auto;
        height: v-bind(height);
        border-radius: v-bind(radius);
        flex: 1 0 auto;
        overflow: hidden;
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
    }
  }
</style>
