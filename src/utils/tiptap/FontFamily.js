// see: https://github.com/scrumpy/tiptap/issues/64
import { Mark } from 'tiptap'
import { updateMark, markInputRule } from 'tiptap-commands'

export default class FontFamily extends Mark {

	get name() {
		return 'fontFamily'
	}

	get schema() {
		return {
			attrs: {
				fontFamily: {
					default: 'arial',
				},
			},
			parseDOM: [{
				style: 'font-family',
				getAttrs: mark => ({ fontFamily: mark })
			}],
			toDOM: mark => ['span', { style: `font-family: ${mark.attrs.fontFamily}` }, 0],
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
