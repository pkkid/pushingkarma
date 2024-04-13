/* eslint-env node */
module.exports = {
  root: true,
  env: {node: true},
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    'semi': ['error', 'never'],
    'vue/comment-directive': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/valid-v-slot': ['error', {allowModifiers: true}]
  }
}
