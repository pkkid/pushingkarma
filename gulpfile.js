// Encoding: UTF-8
// gulp tasks: js, css, codemirror, watch
'use strict';

var gulp = require('gulp');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var merge = require('merge-stream');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var watch = require('gulp-watch');

var nm = function(path) { return './node_modules/'+ path; };
var dist = function(path) { return './pk/static/dist/'+ path };

// Javascript
gulp.task('js', function() {
  return gulp.src('./pk/static/site/js/*.js')
    .pipe(concat('site.js', {newLine:'\n\n\n'}))
    .pipe(gulp.dest(dist('site')));
});


// CSS
gulp.task('css', function() {
  return gulp.src('pk/static/site/css/site.scss')
    .pipe(sourcemaps.init())
    .pipe(sass({style:'expanded'}))
    .on('error', sass.logError)
    .pipe(autoprefixer('last 2 versions', '> 1%'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(dist('site')));
});


// Codemirror
gulp.task('codemirror', function() {
  var streams = merge();
  streams.add(gulp.src([
      nm('codemirror/lib/codemirror.css'),
      nm('codemirror/addon/dialog/dialog.css'),
      nm('codemirror/addon/scroll/simplescrollbars.css'),
      nm('codemirror/theme/blackboard.css'),
      nm('codemirror/theme/solarized.css'),
    ])
    .pipe(concat('codemirror.css', {newLine:'\n\n\n'}))
    .pipe(gulp.dest(dist('codemirror'))));
  streams.add(gulp.src([
      nm('codemirror/lib/codemirror.js'),
      nm('codemirror/addon/dialog/dialog.js'),
      nm('codemirror/addon/edit/continuelist.js'),
      nm('codemirror/addon/mode/overlay.js'),
      nm('codemirror/addon/scroll/simplescrollbars.js'),
      nm('codemirror/addon/search/search.js'),
      nm('codemirror/addon/search/searchcursor.js'),
      nm('codemirror/keymap/sublime.js'),
      nm('codemirror/mode/css/css.js'),
      nm('codemirror/mode/django/django.js'),
      nm('codemirror/mode/gfm/gfm.js'),
      nm('codemirror/mode/javascript/javascript.js'),
      nm('codemirror/mode/markdown/markdown.js'),
      nm('codemirror/mode/python/python.js'),
      nm('codemirror/mode/sass/sass.js'),
      nm('codemirror/mode/xml/xml.js'),
    ])
    .pipe(concat('codemirror.js', {newLine:'\n\n\n'}))
    .pipe(gulp.dest(dist('codemirror'))));
  return streams;
});


// NPM - copy npm resources to dashboard/static/dist
gulp.task('npm', function() {
  return merge(
    gulp.src('./pk/static/site/font/*').pipe(gulp.dest(dist('site/font'))),
    gulp.src('./pk/static/site/img/*').pipe(gulp.dest(dist('site/img'))),
    gulp.src(nm('@mdi/font/css/*min*')).pipe(gulp.dest(dist('mdi/css'))),
    gulp.src(nm('@mdi/font/fonts/*')).pipe(gulp.dest(dist('mdi/fonts'))),
    gulp.src(nm('animate.css/animate.min.css')).pipe(gulp.dest(dist('animate.css'))),
    gulp.src(nm('bootstrap/dist/**/*min*')).pipe(gulp.dest(dist('bootstrap'))),
    gulp.src(nm('clipboard/dist/*min*')).pipe(gulp.dest(dist('clipboard'))),
    gulp.src(nm('handlebars/dist/handlebars.min.js')).pipe(gulp.dest(dist('handlebars'))),
    gulp.src(nm('highcharts/highcharts.js*')).pipe(gulp.dest(dist('highcharts'))),
    gulp.src(nm('highlightjs/highlight.pack.min.js')).pipe(gulp.dest(dist('highlightjs'))),
    gulp.src(nm('jquery-confirm/dist/*min*')).pipe(gulp.dest(dist('jquery-confirm'))),
    gulp.src(nm('jquery-toast-plugin/dist/*min*')).pipe(gulp.dest(dist('jquery-toast-plugin'))),
    gulp.src(nm('jquery-ui-dist/*min*')).pipe(gulp.dest(dist('jquery-ui'))),
    gulp.src(nm('jquery/dist/*min*')).pipe(gulp.dest(dist('jquery'))),
    gulp.src(nm('js-cookie/src/js.cookie.js')).pipe(gulp.dest(dist('js-cookie'))),
    gulp.src(nm('lodash/lodash.min.js')).pipe(gulp.dest(dist('lodash'))),
    gulp.src(nm('moment/min/moment.min.js')).pipe(gulp.dest(dist('moment'))),
    gulp.src(nm('popper.js/dist/umd/*min*')).pipe(gulp.dest(dist('popper.js'))),
    gulp.src(nm('tether/dist/**/*min*')).pipe(gulp.dest(dist('tether'))),
    gulp.src(nm('weather-underground-icons/dist/**/*')).pipe(gulp.dest(dist('wu-icons'))),
  );
})

// Build & Watch
gulp.task('default', gulp.parallel('js', 'css', 'npm', 'codemirror'));
gulp.task('watch', function() {
  gulp.watch(['**/js/*.js', '!**/js/site.js'], gulp.parallel('js'));
  gulp.watch('**/css/*.scss', gulp.parallel('css'));
});
