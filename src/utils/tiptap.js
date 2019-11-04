import {Mark} from 'tiptap';
import {markInputRule, updateMark, removeMark} from 'tiptap-commands';
import {Link as BaseLink} from 'tiptap-extensions';


/**
 * Link - Extends the built in Link from tiptap-extensions to
 * simply top it from opening links when in editing mode.
 */
export class Link extends BaseLink {
  get plugins() {
    return [];
  }
}


/**
 * FontSize - Extends the built in Mark from tiptap allowing
 * the editor to <drumroll> set the font-size.
 */
export class FontSize extends Mark {
  get name() {
    return 'fontSize';
  }
  
  get schema() {
    return {
      attrs: {fontSize: {default: '1em'}},
      parseDOM: [{
        style: 'font-size',
        getAttrs: value => value.indexOf('em') !== -1 ? {fontSize:value} : '',
      }],
      toDOM: mark => ['span', {style:`font-size:${mark.attrs.fontSize}`}, 0],
    };
  }

  commands({type}) {
    return attrs => {
      return attrs.fontSize ? updateMark(type, attrs) : removeMark(type);
    };
  }
  
  inputRules({type}) {
    return [markInputRule(/(?:\*\*|__)([^*_]+)(?:\*\*|__)$/, type)];
  }
}


/**
 * FontColor - Extends the built in Mark from tiptap allowing
 * the editor to set the font color.
 */
export class FontColor extends Mark {
	get name() {
		return 'fontColor';
	}

	get schema() {
		return {
			attrs: {fontColor: {default: '#000000'}},
			parseDOM: [{
				style: 'color',
				getAttrs: mark => mark.indexOf('rgb') !== -1 ? {fontColor: mark} : '',
			}],
			toDOM: mark => ['span', {style:`color:${mark.attrs.fontColor}`}, 0],
		};
	}
	
	commands({type}) {
    return attrs => {
      return attrs.fontColor ? updateMark(type, attrs) : removeMark(type);
    };
  }

	inputRules({ type }) {
		return [markInputRule(/(?:\*\*|__)([^*_]+)(?:\*\*|__)$/, type)];
	}
}
