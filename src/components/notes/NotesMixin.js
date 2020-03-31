import includes from 'lodash/includes';

export default {
  methods: {
    // Is Private Note
    // Returns true is the specified note is private
    isPrivateNote: function(note) {
      return includes(note.tags.toLowerCase(), 'private');
    },
  }
};
