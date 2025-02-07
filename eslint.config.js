import path from 'node:path'
import pluginjs from '@eslint/js'
import {fileURLToPath} from 'node:url'
import {FlatCompat} from '@eslint/eslintrc'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)
const compat = new FlatCompat({
    baseDirectory: dirname,
    recommendedConfig: pluginjs.configs.recommended,
})

export default [
  ...compat.extends('eslint:recommended'),
  ...compat.extends('plugin:vue/vue3-essential'),
  {env: {node: true}},
  {ignores: ['pk/*']},
  {rules: {
    'no-unused-vars': 'off',
    'semi': ['error', 'never'],
    'vue/comment-directive': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/valid-v-slot': ['error', {allowModifiers:true}],
  }}
]
