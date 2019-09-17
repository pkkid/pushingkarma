import { Mark } from 'tiptap'
import { updateMark, markInputRule } from 'tiptap-commands'

export default class FontFillColor extends Mark {

	get name() {
		return 'fontFillColor'
	}

	get schema() {
		return {
			attrs: {
				fontFillColor: {
					default: '#000000',
				},
			},
			parseDOM: [{
				style: 'background-color',
				getAttrs: mark => (mark.indexOf('rgb') !== -1 ? { fontFillColor: mark } : '')
			}],
			toDOM: mark => ['span', { style: `background-color: ${mark.attrs.fontFillColor}` }, 0],
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