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

const site = {
  layout: 'navtop',
};

export default new Vuex.Store({
  plugins: [pathify.plugin],
  modules: {
    site: makeModule(site),
    notes: makeModule(notes),
  },
});
