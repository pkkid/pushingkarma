import Vue from 'vue';
import Vuex from 'vuex';
import notes from './components/notes/NotesStore';
import budget from './components/budget/BudgetStore';
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

export const DEFAULT_USER = {
  id: null,
  email: null,
  firstName: null,
  lastName: null,
  dateJoined: null,
  lastLogin: null,
};

const globals = {
  layout: 'topnav',
  user: DEFAULT_USER,
  avatar: '',
  gauth: null,
};

export default new Vuex.Store({
  plugins: [pathify.plugin],
  modules: {
    global: makeModule(globals),
    notes: makeModule(notes),
    budget: makeModule(budget),
  },
});
