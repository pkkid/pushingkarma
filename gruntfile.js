/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */

module.exports = function(grunt) {
  'use strict';

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
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
    sass: {
      css: {
        options: {
          style: 'compressed',
          cacheLocation: '/tmp/sass-cache',
        },
        files: {
          'pk/static/css/pushingkarma.css': 'pk/static/css/pushingkarma.scss',
        },
      },
    },
    watch: {
      js: {
        files: ['**/*.js'],
        tasks: ['concat:js'],
        options: {
          spawn: false,
        },
      },
      css: {
        files: ['**/*.scss'],
        tasks: ['sass:css'],
        options: {
          spawn: false,
        },
      },
    },
  });

  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');
};
