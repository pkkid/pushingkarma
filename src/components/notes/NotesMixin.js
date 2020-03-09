import * as _ from 'lodash';

export default {
  methods: {

    // Is Private Note
    // Returns true is the specified note is private
    isPrivateNote: function(note) {
      return _.includes(note.tags.toLowerCase(), 'private');
    },
    
  }
};
