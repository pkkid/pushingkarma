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
