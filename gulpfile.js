/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

var gulp = require('gulp');
var autoprefixer = require('gulp-autoprefixer');
var batch = require('gulp-batch');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var watch = require('gulp-watch');


// Javascript
gulp.task('js', function() {
  gulp.src('./pk/static/js/*.js')
  .pipe(concat('pushingkarma.js', {newLine:'\n\n\n'}))
  .pipe(gulp.dest('./pk/static/dist'));
});


// CSS
gulp.task('css', function () {
  gulp.src('pk/static/css/pushingkarma.scss')
  .pipe(sourcemaps.init())
  .pipe(sass({style:'expanded'}))
  .on('error', sass.logError)
  .pipe(autoprefixer('last 2 versions', '> 1%'))
  .pipe(sourcemaps.write('.'))
  .pipe(gulp.dest('./pk/static/dist'));
});


// Codemirror
gulp.task('codemirror-css', function() {
  gulp.src([
    './pk/static/bower/codemirror/lib/codemirror.css',
    './pk/static/bower/codemirror/addon/scroll/simplescrollbars.css',
    './pk/static/bower/codemirror/theme/blackboard.css',
    './pk/static/bower/codemirror/theme/solarized.css',
  ])
  .pipe(concat('codemirror.css', {newLine:'\n\n\n'}))
  .pipe(gulp.dest('./pk/static/dist'));
});
gulp.task('codemirror-js', function() {
  gulp.src([
    './pk/static/bower/codemirror/lib/codemirror.js',
    './pk/static/bower/codemirror/addon/mode/overlay.js',
    './pk/static/bower/codemirror/addon/scroll/simplescrollbars.js',
    './pk/static/bower/codemirror/mode/css/css.js',
    './pk/static/bower/codemirror/mode/django/django.js',
    './pk/static/bower/codemirror/mode/gfm/gfm.js',
    './pk/static/bower/codemirror/mode/javascript/javascript.js',
    './pk/static/bower/codemirror/mode/markdown/markdown.js',
    './pk/static/bower/codemirror/mode/python/python.js',
    './pk/static/bower/codemirror/mode/sass/sass.js',
    './pk/static/bower/codemirror/mode/xml/xml.js',
  ])
  .pipe(concat('codemirror.js', {newLine:'\n\n\n'}))
  .pipe(gulp.dest('./pk/static/dist'));
});


// Watch
gulp.task('watch', function () {
  watch(['**/js/*.js', '!**/js/pushingkarma.js'], batch(function(events, done) {
    gulp.start('js', done);
  }));
  watch('**/css/*.scss', batch(function(events, done) {
    gulp.start('css', done);
  }));
  gulp.start('default');
});


// Default
gulp.task('default', ['js', 'css', 'codemirror-css', 'codemirror-js']);
