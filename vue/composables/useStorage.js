import { ref, watch } from 'vue'

// Use Storage
// Creates a reactive ref that persists its value in localStorage
//  key (string): The localStorage key to store the value under
//  defaultValue (any): The default value if no value exists in localStorage
export function useStorage(key, defaultValue) {
  const storedValue = localStorage.getItem(key)
  const value = ref(storedValue ? JSON.parse(storedValue) : defaultValue)

  // Watch for changes and update localStorage
  watch(value, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue))
  }, { deep: true })

  return value
}
