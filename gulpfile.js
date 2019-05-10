// Encoding: UTF-8
// gulp tasks: js, css, codemirror, watch
'use strict';

var gulp = require('gulp');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var spawn = require('child_process').spawn;
var sourcemaps = require('gulp-sourcemaps');
var react = require('gulp-react');

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

// React
gulp.task('react', function () {
  return gulp.src('pk/static/site/js/app.jsx')
    .pipe(react())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./pk/static/dist/site'));
});

// Runserver
gulp.task('runserver', function() {
  return spawn(process.env.VIRTUAL_ENV +'/bin/python',
    ['pk/manage.py', 'runserver'], {stdio: 'inherit'});
});

// Build & Watch
gulp.task('build', gulp.parallel('js', 'css'));
gulp.task('watch', function() {
  gulp.watch(['**/js/*.js', '!**/js/site.js'], gulp.parallel('js'));
  gulp.watch('**/css/*.scss', gulp.parallel('css'));
});
gulp.task('default', gulp.series('build', gulp.parallel('watch', 'runserver')));
