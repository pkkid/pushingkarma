
export const fixScroll = {
  watch: {
    $route() {
      const currentRoute = this.$router.currentRoute;
      const idToScrollTo = currentRoute.hash;
      this.$nextTick(() => {
        if (idToScrollTo && document.querySelector(idToScrollTo)) {
          document.querySelector(idToScrollTo).scrollIntoView();
        }
      });
    },
  },
};
