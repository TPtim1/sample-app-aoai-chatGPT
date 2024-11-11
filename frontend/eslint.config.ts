/*
* File configures ESLint for the project. Imports global variables for the browser, 
* recommended settings for React and Prettier, and uses FlatCompat for compatibility 
* with ESLint configurations. Exports a configuration array that includes global variables, 
* extensions for TypeScript, React, and Prettier to ensure proper linting of code in the project.
*/

import globals from 'globals'
import pluginReactConfig from 'eslint-plugin-react/configs/recommended.js'
import eslintConfigPrettier from 'eslint-config-prettier'

import path from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'
import pluginJs from '@eslint/js'

// mimic CommonJS variables -- not needed if using CommonJS
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const compat = new FlatCompat({ baseDirectory: __dirname, recommendedConfig: pluginJs.configs.recommended })

export default [
  { languageOptions: { globals: globals.browser } },
  ...compat.extends('standard-with-typescript'),
  pluginReactConfig,
  eslintConfigPrettier
]
