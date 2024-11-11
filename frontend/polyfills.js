/*
* imports and applies the polyfill for the replaceAll method on strings. 
* Polyfill ensures that the replaceAll method will be available even in environments 
* that do not natively support it, increasing code compatibility with different JavaScript 
* versions and browsers.
*/

const replaceAllInserter = require('string.prototype.replaceall')

replaceAllInserter.shim()
