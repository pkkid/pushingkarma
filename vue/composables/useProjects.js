import {computed, ref} from 'vue'
import {Projects} from '@/utils/api'
import {PROJECTS} from '@/views/projects/projects'

// Use Projects
// Singleton composable that merges the project registry with GitHub stats from
// the API. Stats are fetched once per page load and shared by every caller.
export default (function() {
  const repos = ref({})         // GitHub stats keyed by owner/repo
  var request = null            // Pending or completed list request

  // Load
  // Fetch GitHub stats once; a failed request is retried on the next call
  function load() {
    if (request) { return request }
    request = Projects.listRepos().then(function({data}) {
      repos.value = Object.fromEntries(data.map(repo => [repo.name, repo]))
    }).catch(function(err) {
      request = null
      console.error('Unable to load project stats', err)
    })
    return request
  }

  // Projects
  // Registry entries with their GitHub stats under the github key (null until loaded)
  const projects = computed(function() {
    return PROJECTS.map(project => ({...project, github:repos.value[project.repo] || null}))
  })

  return function useProjects() {
    load()
    return {projects}
  }
})()
