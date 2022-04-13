// TipTap Task Item
// Task Items do not work in TipTap if you have Bitwarden or Enpass installed.
// This version of tiptap-task-tem.cjs.js gets around the issue by not using
// real inputs for the task items. TipTav dev isn't interesting in addressing
// the issue as they claim its a Bitwarden bug, and Bitwarden has has the issue
// for three years now. You can read the bug reports here:
//   TapTap: https://github.com/ueberdosis/tiptap/issues/2697
//   Bitwaden: https://github.com/bitwarden/browser/issues/725
//
// If either of the above bugs ever get closed, we can delete this file and
// change the import in Notes.vue to:
//   import TaskList from '@tiptap/extension-task-item';
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var core = require("@tiptap/core");
const inputRegex = /^\s*(\[([ |x])\])\s$/;

const TaskItem = core.Node.create({
  name: "taskItem",
  addOptions() {
    return {
      nested: false,
      HTMLAttributes: {}
    };
  },
  content() {
    return this.options.nested ? "paragraph block*" : "paragraph+";
  },
  defining: true,
  addAttributes() {
    return {
      checked: {
        default: false,
        keepOnSplit: false,
        parseHTML: (element) => element.getAttribute("data-checked") === "true",
        renderHTML: (attributes) => ({"data-checked": attributes.checked})
      }
    };
  },
  parseHTML() {
    return [{
      tag: `li[data-type="${this.name}"]`,
      priority: 51
    }];
  },
  renderHTML({HTMLAttributes}) {
    return [
      "li",
      core.mergeAttributes(
        this.options.HTMLAttributes,
        HTMLAttributes,
        {"data-type": this.name}),
      ["label", ["span"]],
      ["div", 0]
    ];
  },
  addKeyboardShortcuts() {
    const shortcuts = {
      Enter: () => this.editor.commands.splitListItem(this.name),
      "Shift-Tab": () => this.editor.commands.liftListItem(this.name)
    };
    if (!this.options.nested) {
      return shortcuts;
    }
    return {
      ...shortcuts,
      Tab: () => this.editor.commands.sinkListItem(this.name)
    };
  },
  addNodeView() {
    return ({ node, HTMLAttributes, getPos, editor }) => {
      const listItem = document.createElement("li");
      const checkboxWrapper = document.createElement("label");
      const checkboxStyler = document.createElement("span");
      const content = document.createElement("div");
      checkboxWrapper.contentEditable = "false";
      checkboxWrapper.addEventListener("click", () => {
        // If the editor isn’t editable break early
        if (!editor.isEditable) {
          return;
        }
        // reverse the value
        const checked = listItem.dataset.checked !== "true";
        if (editor.isEditable && typeof getPos === "function") {
          editor
            .chain()
            .focus(undefined, { scrollIntoView: false })
            .command(({ tr }) => {
              const position = getPos();
              const currentNode = tr.doc.nodeAt(position);
              tr.setNodeMarkup(position, undefined, {
                ...(currentNode === null || currentNode === void 0
                  ? void 0
                  : currentNode.attrs),
                checked
              });
              return true;
            })
            .run();
        }
      });
      Object.entries(this.options.HTMLAttributes).forEach(([key, value]) => {
        listItem.setAttribute(key, value);
      });
      listItem.dataset.checked = node.attrs.checked;
      checkboxWrapper.append(checkboxStyler);
      listItem.append(checkboxWrapper, content);
      Object.entries(HTMLAttributes).forEach(([key, value]) => {
        listItem.setAttribute(key, value);
      });
      return {
        dom: listItem,
        contentDOM: content,
        update: (updatedNode) => {
          if (updatedNode.type !== this.type) {
            return false;
          }
          listItem.dataset.checked = updatedNode.attrs.checked;
          return true;
        }
      };
    };
  },
  addInputRules() {
    return [
      core.wrappingInputRule({
        find: inputRegex,
        type: this.type,
        getAttributes: (match) => ({
          checked: match[match.length - 1] === "x"
        })
      })
    ];
  }
});

exports.TaskItem = TaskItem;
exports["default"] = TaskItem;
exports.inputRegex = inputRegex;
