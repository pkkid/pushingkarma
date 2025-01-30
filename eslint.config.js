import globals from 'globals'
import path from 'node:path'
import js from '@eslint/js'
import {fileURLToPath} from 'node:url'
import {FlatCompat} from '@eslint/eslintrc'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)
const compat = new FlatCompat({
    baseDirectory: dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
})

export default [
  ...compat.extends('plugin:vue/vue3-essential', 'eslint:recommended'), {
  languageOptions: {
    globals: {...globals.node},
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'no-unused-vars': 'off',
    'semi': ['error', 'never'],
    'vue/comment-directive': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/valid-v-slot': ['error', {allowModifiers:true}],
  },
}]