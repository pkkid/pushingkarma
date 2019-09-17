<template>
    <div class="editor">
        <editor class="editor" :extensions="extensions" @update="$emit('update', $event)" @init="inited" :editable="true" :watchDoc="true" ref="editor">
            <div class="menububble" slot="menububble" slot-scope="{ nodes, marks, focus }">
                <template v-if="marks">

                    <q-btn-dropdown :content-style="popoverStyle" label="B" text-color="white" dense no-caps no-wrap>
                        <button class="menububble__button" :class="{ 'is-active': marks.bold.active() }" @click="marks.bold.command">
                            <q-icon name="format_bold" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.italic.active() }" @click="marks.italic.command">
                            <q-icon name="format_italic" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.underline.active() }" @click="marks.underline.command">
                            <q-icon name="format_underlined" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.strike.active() }" @click="marks.strike.command">
                            <q-icon name="format_strikethrough" />
                        </button>
                    </q-btn-dropdown>

                    <q-btn-dropdown :content-style="popoverStyle" icon="format_list_bulleted" text-color="white" dense no-caps no-wrap>
                        <button class="menububble__button" :class="{ 'is-active': nodes.bullet_list.active() }" @click="nodes.bullet_list.command">
                            <q-icon name="format_list_bulleted" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': nodes.ordered_list.active() }" @click="nodes.ordered_list.command" >
                            <q-icon name="format_list_numbered" />
                        </button>
                    </q-btn-dropdown>

                    <q-btn-dropdown :content-style="popoverStyle" icon="format_align_center" text-color="white" dense no-caps no-wrap>
                        <button class="menububble__button" :class="{ 'is-active': nodes.paragraph.active({ textAlign: 'left' }) }" @click="nodes.paragraph.command({ textAlign: 'left' })" >
                            <q-icon name="format_align_left" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': nodes.paragraph.active({ textAlign: 'center' }) }" @click="nodes.paragraph.command({ textAlign: 'center' })" >
                            <q-icon name="format_align_center" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': nodes.paragraph.active({ textAlign: 'right' }) }" @click="nodes.paragraph.command({ textAlign: 'right' })" >
                            <q-icon name="format_align_right" />
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': nodes.paragraph.active({ textAlign: 'justify' }) }" @click="nodes.paragraph.command({ textAlign: 'justify' })" >
                            <q-icon name="format_align_justify" />
                        </button>
                    </q-btn-dropdown>
                    
                    <!-- FONT SIZE -->
                    <q-btn-dropdown :content-style="popoverStyle" icon="format_size" text-color="white" dense no-caps no-wrap>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '0.9em'}" @click="marks.fontSize.command({ fontSize: '0.9em' })" >
                            18
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1em' || !('fontSize' in marks.fontSize.attrs) }" @click="marks.fontSize.command({ fontSize: '1em' })" >
                            20
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1.1em' }" @click="marks.fontSize.command({ fontSize: '1.1em' })" >
                            22
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1.2em' }" @click="marks.fontSize.command({ fontSize: '1.2em' })" >
                            24
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1.4em' }" @click="marks.fontSize.command({ fontSize: '1.4em' })" >
                            28
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1.6em'}" @click="marks.fontSize.command({ fontSize: '1.6em' })" >
                            32
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '1.9em'}" @click="marks.fontSize.command({ fontSize: '1.9em' })" >
                            38
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '2.1em'}" @click="marks.fontSize.command({ fontSize: '2.1em' })" >
                            42
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '2.4em'}" @click="marks.fontSize.command({ fontSize: '2.4em' })" >
                            48
                        </button>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontSize.attrs.fontSize === '2.7em'}" @click="marks.fontSize.command({ fontSize: '2.7em' })" >
                            54
                        </button>
                    </q-btn-dropdown>

                    <!-- FONT FAMILY -->
                    <q-btn-dropdown :content-style="popoverStyle" :label="'Font: ' + (marks.fontFamily.attrs.fontFamily || 'Default Arial')" text-color="white" dense no-caps no-wrap>
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'arial' || marks.fontFamily.attrs.fontFamily === 'arial, sans-serif' }" @click="marks.fontFamily.command({ fontFamily: 'arial, sans-serif' })" >
                            Default Arial
                        </button><br />
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'verdana' || marks.fontFamily.attrs.fontFamily === 'verdana, sans-serif' }" @click="marks.fontFamily.command({ fontFamily: 'verdana, sans-serif' })" >
                            Verdana
                        </button><br />
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'helvetica' || marks.fontFamily.attrs.fontFamily === 'helvetica, sans-serif' }" @click="marks.fontFamily.command({ fontFamily: 'helvetica, sans-serif' })" >
                            Helvetica
                        </button><br />
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'times' || marks.fontFamily.attrs.fontFamily === 'times, serif' }" @click="marks.fontFamily.command({ fontFamily: 'times, serif' })" >
                            Times
                        </button><br />
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'georgia' || marks.fontFamily.attrs.fontFamily === 'georgia, serif' }" @click="marks.fontFamily.command({ fontFamily: 'georgia, serif' })" >
                            Georgia
                        </button><br />
                        <button class="menububble__button" :class="{ 'is-active': marks.fontFamily.attrs.fontFamily === 'courier' || marks.fontFamily.attrs.fontFamily === 'courier, monospace' }" @click="marks.fontFamily.command({ fontFamily: 'courier, monospace' })" >
                            Courier
                        </button>
                    </q-btn-dropdown>

                    <!-- FONT COLOR -->
                    <q-btn-dropdown :content-style="popoverStyle" icon="format_color_text" text-color="white" dense no-caps no-wrap>
                        <swatch :value="('fontTextColor' in marks.fontTextColor.attrs) ? marks.fontTextColor.attrs.fontTextColor : '#000000'" @input="marks.fontTextColor.command({ fontTextColor: $event })" />
                    </q-btn-dropdown>

                    <!-- FONT BG COLOR -->
                    <q-btn-dropdown :content-style="popoverStyle" icon="format_color_fill" text-color="white" dense no-caps no-wrap>
                        <swatch :value="('fontFillColor' in marks.fontFillColor.attrs) ? marks.fontFillColor.attrs.fontFillColor : '#000000'" @input="marks.fontFillColor.command({ fontFillColor: $event })" />
                    </q-btn-dropdown>
                </template>
            </div>

            <!-- Add HTML to the scoped slot called `content` -->
            <div class="editor__content" slot="content" slot-scope="props" >
                <span v-html="text" />
            </div>
        </editor>

        <div v-if="showSuggestions" slot="menububble" class="suggestList" ref="suggestions" >
            <template>
                <button v-for="user in filteredUsers" :key="user.id" class="menububble__button" @click="selectUser(user)" >
                    {{user.name}}
                </button>
            </template>
        </div>
    </div>
</template>

<script>
import { Editor } from 'tiptap'
import {
  // Nodes
  BlockquoteNode, BulletListNode, HardBreakNode, HeadingNode, ListItemNode, OrderedListNode,
  // Marks
  BoldMark, ItalicMark, StrikeMark, UnderlineMark,
  // General Extensions
  HistoryExtension, MentionNode
} from 'tiptap-extensions'
import ParagraphAlignmentNode from './editorExtensions/Paragraph.js'
import FormatFontSize from './editorExtensions/FontSize.js'
import FormatFontFamily from './editorExtensions/FontFamily.js'
import FormatFontTextColor from './editorExtensions/FontTextColor.js'
import FormatFontFillColor from './editorExtensions/FontFillColor.js'
import FormatFontFunctions from './editorExtensions/FontFunctions.js'
import swatch from './swatchColors'

export default {
    components: { Editor, swatch },
    props: { 
        text: {required: false, type: String, default: 'Type some text...'}
    },
    data () {
        return {
            extensions: [
                new BlockquoteNode(),
                new BulletListNode(),
                new HardBreakNode(),
                new HeadingNode({ maxLevel: 3 }),
                new ListItemNode(),
                new OrderedListNode(),
                new BoldMark(),
                new ItalicMark(),
                new StrikeMark(),
                new UnderlineMark(),
                new HistoryExtension(),
                new ParagraphAlignmentNode(),
                new FormatFontSize(),
                new FormatFontFamily(),
                new FormatFontTextColor(),
                new FormatFontFillColor(),
                new FormatFontFunctions()
            ],
            popoverStyle: {
                'background-color': '#000',
                'border-radius': '5px',
                'border': '1px solid grey',
                '-webkit-box-shadow': '0px 0px 5px 0px lightgrey',
                '-moz-box-shadow': '0px 0px 5px 0px lightgrey',
                'box-shadow': '0px 0px 5px 0px lightgrey',
                'margin-bottom': '.5rem',
                'padding': '.3rem'
            }
        }
    },
    methods: {
        inited(event) {
            this.$emit('init', event)
            var self = this
            event.view.dom.addEventListener('blur', function() {
                self.$emit('blured')
            });
        }
    }
}
</script>

<style scoped>

.menububble {
	-ms-transform: translateX(-50%);
	-webkit-transform: translateX(-50%);
	-webkit-transition: opacity.2s, visibility.2s;
	background:  #000;
	border-radius: 5px;
    border: 1px solid grey;
    -webkit-box-shadow: 0px 0px 5px 0px lightgrey;
    -moz-box-shadow: 0px 0px 5px 0px lightgrey;
    box-shadow: 0px 0px 5px 0px lightgrey;
	display: -webkit-box;
	display: -ms-flexbox;
	display: flex;
	margin-bottom: .5rem;
	opacity: 0;
	padding: .3rem;
	position: absolute;
	transform: translateX(-50%);
	transition: opacity.2s, visibility.2s;
	visibility: hidden;
	z-index: 20
}
.menububble__button {
	background: rgba(0, 0, 0, 0);
	border: 0;
	border-radius: 3px;
	color:  #fff;
	cursor: pointer;
	display: -webkit-inline-box;
	display: -ms-inline-flexbox;
	display: inline-flex;
	margin-right: .2rem;
	padding: .2rem .5rem;
}
.menububble__button:last-child {
	margin-right: 0;
}
.menububble__button:hover {
	background-color: hsla(0, 0%, 100%, .1);
}
.menububble__button.is-active {
	background-color: hsla(0, 0%, 100%, .2);
}
.menububble__form {
	-ms-flex-align: center;
	-webkit-box-align: center;
	align-items: center;
	display: -webkit-box;
	display: -ms-flexbox;
	display: flex;
}
.menububble__input {
	background: rgba(0, 0, 0, 0);
	border: none;
	color:  #fff;
	font: inherit;
}


</style>
