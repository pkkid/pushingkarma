import globals from 'globals'
import pluginjs from '@eslint/js'
import pluginvue from 'eslint-plugin-vue'

export default [
  pluginjs.configs.recommended,
  ...pluginvue.configs['flat/essential'],
  {ignores: ['pk/*', '.venv/*']},
  {languageOptions: { globals: {
    ...globals.browser,
    process:'readonly'
  }}},
  {rules: {
    'no-unused-vars': 'off',
    'semi': ['error', 'never'],
    'vue/comment-directive': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/use-v-on-exact': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/valid-v-slot': ['error', {allowModifiers:true}],
  }},
]
