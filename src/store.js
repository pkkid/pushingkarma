import Vue from 'vue'
import Vuex from 'vuex'
import notes from './components/notes/store'
import pathify from 'vuex-pathify'
import {make} from 'vuex-pathify'
import {forEach} from 'lodash'
Vue.use(Vuex)

const site = {
  layout: 'navtop',
}

var modules = {}
forEach({site, notes}, function(store, name) {
  modules[name] = {
    namespaced: true,
    state: store,
    getters: make.getters(store),
    actions: make.actions(store),
    mutations: make.mutations(store),
  }
})

export default new Vuex.Store({
  plugins: [pathify.plugin],
  modules: modules,
})
