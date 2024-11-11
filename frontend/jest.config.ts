/*
* configures Jest for testing in the project. Defines configuration options such as verbose test 
* output (verbose: true), using ts-jest to transform TypeScript files, and setting files after 
* environment initialization (setupFilesAfterEnv) to ensure tests run correctly.
*/

import type { Config } from '@jest/types'

const config: Config.InitialOptions = {
  verbose: true,
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  setupFilesAfterEnv: ['<rootDir>/polyfills.js']
}

export default config
