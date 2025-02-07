
// Set apibase URL to port 8000 if running in development mode.
// This is the port that the Django runserver uses.
export const apibase = process.env.NODE_ENV === 'development' ?
  `http://${window.location.hostname}:8000/api` :
  `http://${window.location.hostname}/api`


// Pop
// Remove and return an item from an object
export function pop(obj, key) {
  if (Object.prototype.hasOwnProperty.call(obj, key)) {
    const value = obj[key]
    delete obj[key]
    return value
  }
  return null
}
