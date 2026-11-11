<template>
  <div id='projectlist'>
    <div class='header'>
      <span>Projects</span>
      <PillSelect v-model='sortby' :options='SORTS' aria-label='Sort projects'/>
    </div>
    <ul>
      <li v-for='project in sorted' :key='project.slug'>
        <router-link :to='`/projects/${project.slug}`' :class='{on:project.slug == route.params.slug}'>
          <ProjectIcon :project='project' :colored='false'/>
          <span class='name'>{{project.name}}</span>
          <span class='stat'>{{stat(project)}}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {useRoute} from 'vue-router'
  import {PillSelect} from '@/components'
  import {useProjects, useStorage} from '@/composables'
  import {utils} from '@/utils'
  import ProjectIcon from './ProjectIcon.vue'

  const route = useRoute()
  const {projects} = useProjects()
  const sortby = useStorage('projectlist.sortby', 'stars')   // Sort order {stars, recent}
  const SORTS = [{id:'stars', label:'Popular'}, {id:'recent', label:'Recent'}]  // Sort pill options

  // Sorted
  // Projects by stars (then name), or by most recent push
  const sorted = computed(function() {
    return [...projects.value].sort(function(a, b) {
      if (sortby.value == 'recent') { return pushed(b) - pushed(a) }
      return (b.github?.stars || 0) - (a.github?.stars || 0) || a.name.localeCompare(b.name)
    })
  })

  // Pushed
  // Time of the last push in milliseconds, or 0 when stats are not loaded
  function pushed(project) {
    return project.github?.pushed ? new Date(project.github.pushed).getTime() : 0
  }

  // Stat
  // Star count when sorting by popularity, time since the last push otherwise
  function stat(project) {
    if (!project.github) { return '' }
    if (sortby.value == 'recent') { return utils.timeAgo(pushed(project), true) }
    return project.github.stars ? `★ ${utils.intComma(project.github.stars)}` : ''
  }
</script>

<style>
  #projectlist {
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    min-height: 0px;
    .header {
      align-items: center;
      display: flex;
      justify-content: space-between;
      padding: 0px 15px 10px 18px;
      span {
        color: var(--darkbg-fg4);
        font-family: var(--fontfamily-article);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
      }
    }
    ul {
      list-style: none;
      margin: 0px;
      opacity: 0.7;
      overflow-y: auto;
      padding: 0px 0px 30px 0px;
      scrollbar-gutter: stable;
      transition: opacity 0.5s ease;
      /* Dimmed until hovered or focused, same as the notes search results */
      &:hover, &:has(:focus) { opacity: 1; }
    }
    /* Rows match the notes search results: full width of the panel, article font,
     * muted text, and an accent bar on the left when hovered or selected. */
    li a, li a:hover {
      align-items: center;
      border-left: 3px solid transparent;
      color: var(--darkbg-fg3);
      display: grid;
      font-family: var(--fontfamily-article);
      font-size: 12px;
      gap: 8px;
      grid-template-columns: 1.3em minmax(0px, 1fr) auto;
      padding: 7px 15px;
      text-decoration: none;
      transition: all 0.3s ease;
      .projecticon { color:var(--darkbg-fg1); font-size:1.3em; line-height:1; }
      .name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .stat { color:var(--darkbg-fg4); font-family:var(--fontfamily-code); font-size:11px; }
    }
    li a:hover, li a:focus, li a.on {
      background-color: #fff1;
      border-left: 3px solid var(--accent);
      color: var(--fgcolor);
    }
  }
</style>
