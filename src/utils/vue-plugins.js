import {contains} from './utils.js';

export const fixScroll = {
  watch: {
    $route() {
      // This is very website specific. The two methods to below to scroll
      // items into view depend greatly on which page we are one.
      // 1. If we are scrolling into view after finding the element by its
      //    initial text (using the contains) functions, we will account for
      //    the site's fixed header and use window.scroll to get to the item.
      // 2. Assume the #hash element exists with the proper id, we will use
      //    the standard scrollIntoView() function as we expect the margins
      //    on scrolled elements and their container to be setup properly.
      var hash = this.$router.currentRoute.hash;
      var lookup = hash.toLowerCase().replace('#','');
      lookup = '^'+ lookup.replace(/_/g, '\\s') +'$';
      var elem = contains('h1,h2,h3', lookup);
      if ((hash && elem) || (hash == '#title')) {
        // 1. Scroll to the item containing text.
        // console.log('Scrolling to item containing: '+ lookup);
        this.$nextTick(() => {
          var top = hash == '#title' ? 1 : elem.offsetTop + 150;
          window.scroll({top:top, behavior:'smooth'});
        });
      } else if (hash) {
        // 2. Scroll to the item with #hash id.
        // console.log('Scrolling to #'+ hash);
        this.$nextTick(() => {
          elem = document.querySelector(hash);
          if (elem) { elem.scrollIntoView(); }
        });
      }
    }
  }
};
