/*
* This file is used to export all the api functions and models (from the ./api and ./models)
* so that they can be imported from a single file.
* This is useful when we have a lot of api functions and models
* and we want to import them from a single file.
* This means that anything exported from ./api and ./models will also be available as exports 
* from frontend/src/api/index.ts. This is often used to create a single entry point for multiple modules, 
* making it easier to import them elsewhere in the application.
*/

export * from './api'
export * from './models'
