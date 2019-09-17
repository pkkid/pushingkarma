import Vue from 'vue';
import Vuex from 'vuex';
import notes from './components/notes/NotesStore';
import pathify from 'vuex-pathify';
import {make} from 'vuex-pathify';
Vue.use(Vuex);

var makeModule = function(store) {
  return {
    namespaced: true,
    state: store,
    getters: make.getters(store),
    actions: make.actions(store),
    mutations: make.mutations(store),
  };
};

const global = {
  layout: 'navtop',
  user: {},
};

export default new Vuex.Store({
  plugins: [pathify.plugin],
  modules: {
    global: makeModule(global),
    notes: makeModule(notes),
  },
});
