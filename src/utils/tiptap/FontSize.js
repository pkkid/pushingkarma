import { Mark } from 'tiptap'
import { markInputRule, updateMark } from 'tiptap-commands'

export default class FontSize extends Mark {

	get name() {
		return 'fontSize'
	}

	get schema() {
		return {
			attrs: {
				fontSize: {
					default: '1em',
				},
			},
			parseDOM: [{
				style: 'font-size',
				//getAttrs: mark => ({ fontSize: 'fontSize' in mark.style ? mark.style.fontSize : '' })
				getAttrs: mark => mark.indexOf('em') !== -1 ? { fontSize: mark } : ''
			}],
			toDOM: mark => ['span', { style: `font-size: ${mark.attrs.fontSize}` }, 0],
		}
	}
	
	command({ type, attrs }) {
		return updateMark(type, attrs)
	}

	inputRules({ type }) {
		return [
			markInputRule(/(?:\*\*|__)([^*_]+)(?:\*\*|__)$/, type),
		]
	}
}