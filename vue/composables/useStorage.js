import { ref, watch, onMounted } from 'vue'

// Use Storage
// Creates a reactive ref that persists its value in localStorage
//  key (string): The localStorage key to store the value under
//  defaultValue (any): The default value if no value exists in localStorage
export function useStorage(key, defaultValue) {
  const storedValue = localStorage.getItem(key)
  const value = ref(storedValue ? JSON.parse(storedValue) : defaultValue)

  // Watch for changes and update localStorage
  watch(value, function(newval) {
    localStorage.setItem(key, JSON.stringify(newval))
  }, {deep:true})

  return value
}
