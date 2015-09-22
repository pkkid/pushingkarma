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
  gulp.src([
      './pk/static/js/pk.utils.js',
      './pk/static/js/pk.plugins.js',
      './pk/static/js/pk.login.js',
      './pk/static/js/pk.init.js',
    ])
    .pipe(concat('pushingkarma.js', {newLine:'\n\n\n'}))
    .pipe(gulp.dest('./pk/static/js'));
});


// CSS
gulp.task('sass', function () {
  gulp.src('pk/static/css/pushingkarma.scss')
    .pipe(sourcemaps.init())
    .pipe(sass({style:'expanded'}))
    .pipe(sass().on('error', sass.logError))
    .pipe(autoprefixer('last 2 versions', '> 1%'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./pk/static/css'));
});


// Watch
gulp.task('watch', function () {
  watch(['**/js/*.js', '!**/js/pushingkarma.js'], batch(function(events, done) {
    gulp.start('js', done);
  }));
  watch('**/css/*.scss', batch(function(events, done) {
    gulp.start('sass', done);
  }));
});


// Default
gulp.task('default', ['js', 'sass']);
