/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */

module.exports = function(grunt) {
  'use strict';

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    
    // Concat
    concat: {
      options: {
        separator: '\n\n\n'
      },
      js: {
        src: [
          'pk/static/js/particles.js',
          'pk/static/js/init.js',
        ],
        dest: 'pk/static/js/pushingkarma.js',
      },
    },

    // Sass
    sass: {
      css: {
        options: {
          style: 'expanded',
          cacheLocation: '/tmp/sass-cache',
        },
        files: {
          'pk/static/css/pushingkarma.css': 'pk/static/css/pushingkarma.scss',
        },
      },
    },

    // PostCSS
    postcss: {
      options: {
        map: true,
        processors: [
          require('autoprefixer')({
            browsers: ['last 2 versions']
          })
        ],
      },
      dist: {
        src: 'pk/static/css/pushingkarma.css'
      },
    },

    // Watch
    watch: {
      js: {
        files: ['**/js/*.js'],
        tasks: ['concat:js'],
        options: {
          spawn: false,
          debounceDelay: 0,
        },
      },
      css: {
        files: ['**/css/*.scss'],
        tasks: ['sass:css', 'postcss'],
        options: {
          spawn: false,
          debounceDelay: 0,
        },
      },
    },
  });

  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-postcss');
  grunt.registerTask('default', ['concat', 'sass', 'postcss']);
};
