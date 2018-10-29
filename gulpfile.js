// Encoding: UTF-8
// gulp tasks: js, css, codemirror, watch
'use strict';

var gulp = require('gulp');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var watch = require('gulp-watch');

// Javascript
gulp.task('js', function() {
  return gulp.src('./pk/static/site/js/*.js')
    .pipe(concat('site.js', {newLine:'\n\n\n'}))
    .pipe(gulp.dest('./pk/static/dist/site'));
});

// CSS
gulp.task('css', function() {
  return gulp.src('pk/static/site/css/site.scss')
    .pipe(sourcemaps.init())
    .pipe(sass({style:'expanded'}))
    .on('error', sass.logError)
    .pipe(autoprefixer('last 2 versions', '> 1%'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./pk/static/dist/site'));
});

// Build & Watch
gulp.task('build', gulp.parallel('js', 'css'));
gulp.task('watch', function() {
  gulp.watch(['**/js/*.js', '!**/js/site.js'], gulp.parallel('js'));
  gulp.watch('**/css/*.scss', gulp.parallel('css'));
});
gulp.task('default', gulp.series('build', 'watch'));
