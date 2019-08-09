import Vue from 'vue'
import Vuex from 'vuex'
import pathify from './pathify'
import { make } from 'vuex-pathify'
Vue.use(Vuex)

const state = {
  layout: 'navtop',
}

export default new Vuex.Store({
  plugins: [pathify.plugin],
  state: state,
  mutations: make.mutations(state),
})
