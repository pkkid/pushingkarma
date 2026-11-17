// Cache
// Values saved in localStorage so the new tab page can paint the last known bookmarks
// and wallpaper instantly, then replace them with fresh data from the server. Storage
// can be blocked or full (private windows, partitioned frames), so failures are ignored.

// Get
// Return the cached value for key, or defaultValue when missing or unreadable
export const get = function(key, defaultValue=null) {
  try {
    const value = localStorage.getItem(key)
    return value === null ? defaultValue : JSON.parse(value)
  } catch {
    return defaultValue
  }
}

// Set
// Save value to the cache under key
export const set = function(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* storage unavailable */ }
}
