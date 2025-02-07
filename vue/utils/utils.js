
// Set apibase URL to port 8000 if running in development mode.
// This is the port that the Django runserver uses.
export const apibase = process.env.NODE_ENV === 'development' ?
  `http://${window.location.hostname}:8000/api` :
  `http://${window.location.hostname}/api`
