

/**
 * Format the specified template with the key/value object mapping.
 * @param {str} tmpl - String to format with vars specified by curly brackets {var}.
 * @param {obj} map - Object of key->value pairs to replace in the template string.
 */
export function strfmt(tmpl, map) {
  for (let key in map) {
    tmpl.replace(`{${key}}`, map[key], 'g')
  }
  return tmpl
}
