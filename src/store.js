import Vue from 'vue'
import Vuex from 'vuex'
import pathify from './pathify'
import { make } from 'vuex-pathify'
Vue.use(Vuex)

const state = {
  layout: 'navtop',
  notes_search: '',
  notes_list: [],
}

export default new Vuex.Store({
  mutations: make.mutations(state),
  plugins: [pathify.plugin],
  state: state,
})
