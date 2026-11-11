// Projects
// Display details for each project shown on the site. GitHub stats (stars, forks,
// commit history) are merged in by the useProjects composable from the database,
// which the hourly update_projects command keeps current. When adding a project, also
// add its repo to PROJECTS_GITHUB_REPOS in pk/settings.py so the sync picks it up.
// Each project's icon and color live in the database (GithubRepo.icon and color) so
// the sidebar and home page always show the same icon.
//   slug: Url of the project page (/projects/<slug>)
//   name, repo, tagline: Display name, GitHub owner/repo and a one line description
//   section: 'recent' or 'small' to list the project on the home page
//   banner: Filename of the header image in public/static/img/backgrounds. Where it
//     was taken is read from the image metadata (see list_backgrounds in main/api.py).
//   bannerY: Vertical position of the banner image, 0 (top) to 100 (bottom), default 50
//   website: Link to a dedicated website for the project
//   install: Install command shown in the project page side panel
//   screenshot: {src, caption} image in public/static/img/projects shown in the side panel
//   contributors: Number of top contributors to call out in the side panel (my own
//     accounts are left out). Omit to hide the contributors card.
//   page: Lazy import of a component with the writeup or demo. Projects without
//     one get a short page built from the tagline and GitHub description.

// Language Colors
// Gruvbox colors for the language dot shown next to a project's language
export const LANGUAGE_COLORS = {
  Dart:'#689d6a', JavaScript:'#d79921', Lua:'#b16286', Python:'#458588',
  Rust:'#d65d0e', TypeScript:'#83a598', Vue:'#98971a',
}

export const PROJECTS = [
  {slug:'conky-pkmeter', name:'Conky PKMeter', repo:'pkkid/conky-pkmeter', section:'small',
    banner:'thailand-2011-field.jpg',
    screenshot:{src:'conky-pkmeter.png', caption:'My sidebar as it runs today.'},
    tagline:'A Conky desktop dashboard written in Lua with system, weather, media and AI usage widgets. The successor to PKMeter.',
    page:() => import('./pages/ConkyPkmeter.vue')},
  {slug:'dalica', name:'Dalica', repo:'pkkid/dalica', section:'recent',
    banner:'brazil-2009-cave.jpg',
    tagline:'A local-first photo manager written in Rust. A modern tribute to the classic Picasa workflow.',
    page:() => import('./pages/Dalica.vue')},
  {slug:'puzzle-a-day', name:'Puzzle a Day', repo:'pkkid/puzzle-a-day', section:'small',
    banner:'thailand-2026-ricefield.jpg',
    screenshot:{src:'puzzle-a-day.jpg', caption:'The original A Puzzle a Day from Dragonfjord.'},
    tagline:'Solving the A Puzzle a Day calendar puzzle, from Algorithm X in Python to a Rust and WebAssembly solver.',
    page:() => import('./pages/PuzzleADay.vue')},
  {slug:'vowelit', name:'Vowelit', repo:'pkkid/vowelit', section:'recent', website:'https://vowelit.pkarma.com',
    banner:'thailand-2026-water.jpg',
    tagline:'A word game for Android, iOS and the web. Find words on a letter grid solo, or challenge your friends.',
    page:() => import('./pages/Vowelit.vue')},
  {slug:'x11pygrid', name:'x11 PyGrid', repo:'pkkid/x11pygrid', install:'pip install x11pygrid',
    banner:'thailand-2026-teafield.jpg',
    tagline:'Easily organize open windows by tiling and positioning them to make the best use of your desktop.',
    page:() => import('./pages/X11pygrid.vue')},
  {slug:'pksthemes', name:'PKsThemes', repo:'pkkid/vscode-pksthemes', section:'small',
    banner:'skiing-2026-mtns.jpg',
    tagline:'My high contrast editor themes, available for VSCode, Zed and Sublime Text.'},
  {slug:'claude-aitools', name:'Claude AITools', repo:'pkkid/claude-aitools', section:'recent',
    banner:'thailand-2026-mtntemple.jpg',
    tagline:'A Claude Code mod that adds a slim bar showing usage and cost, plus task checklists and branch cleanup.'},
  {slug:'django-searchquery', name:'Django Searchquery', repo:'pkkid/django-searchquery', section:'small',
    banner:'brazil-2009-mtns2.jpg',
    tagline:'Provides advanced search and filtering capabilities to structured data in Django models.'},
  {slug:'chrome-newtab', name:'Chrome New Tab', repo:'pkkid/chrome-newtab', section:'small',
    banner:'thailand-2026-sunset.jpg', bannerY:100,
    tagline:'Set a custom URL or local html file as the new tab page in Chrome.'},
  {slug:'link-manager', name:'Link Manager', repo:'pkkid/link-manager', section:'small',
    banner:'cruise-2025-carribean.jpg',
    tagline:'Collection of scripts to help easily sync specific configuration files across all your Linux computers.'},
  {slug:'pks-movie-database', name:'PKs Movie Database', repo:'pkkid/pks-movie-database',
    banner:'thailand-2026-waterfall.jpg',
    tagline:'A blast from the past.'},
  {slug:'colorpecker', name:'Colorpecker', repo:'pkkid/colorpecker', section:'small',
    banner:'brazil-2009-sunset.jpg',
    tagline:'A color picker written with PySide6 and QT.'},
  {slug:'django-dbbackup', name:'Django DBBackup', repo:'Archmonger/django-dbbackup', install:'pip install django-dbbackup',
    contributors:5,
    banner:'brazil-2009-mtns.jpg',
    tagline:'Back up and restore your Django database using its native tools, to local disk, Amazon S3, Dropbox and more.',
    page:() => import('./pages/DjangoDbbackup.vue')},
  {slug:'python-plexapi', name:'Python PlexAPI', repo:'pushingkarmaorg/python-plexapi', section:'recent', install:'pip install plexapi',
    contributors:5,
    banner:'thailand-2026-temple.jpg', bannerY:15,
    tagline:'Python bindings for the Plex API. Navigate and manage your local or remote shared libraries.',
    page:() => import('./pages/PythonPlexapi.vue')},
  {slug:'pushingkarma', name:'PushingKarma', repo:'pkkid/pushingkarma',
    banner:'china-2007-landscape.png',
    tagline:'The Django, Django Ninja and Vue source for this website.'},
]

// Banner Style
// Background style for a project's banner image, or an empty style when the project
// has no banner (the banner then shows the striped placeholder).
export function bannerStyle(project) {
  if (!project.banner) { return {} }
  return {
    backgroundImage: `url(/static/img/backgrounds/${project.banner})`,
    backgroundPosition: `center ${project.bannerY ?? 50}%`,
  }
}
