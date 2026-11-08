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
//   banner, credit: Header image url for the project page and where it was taken
//   website: Link to a dedicated website for the project
//   install: Install command shown in the project page side panel
//   page: Lazy import of a component with the writeup or demo. Projects without
//     one get a short page built from the tagline and GitHub description.
// Language Colors
// Gruvbox colors for the language dot shown next to a project's language
export const LANGUAGE_COLORS = {
  Dart:'#689d6a', JavaScript:'#d79921', Lua:'#b16286', Python:'#458588',
  Rust:'#d65d0e', TypeScript:'#83a598', Vue:'#98971a',
}

export const PROJECTS = [
  {slug:'dalica', name:'Dalica', repo:'pkkid/dalica', section:'recent',
    tagline:'A local-first photo manager written in Rust. A modern tribute to the classic Picasa workflow.',
    page:() => import('./pages/Dalica.vue')},
  {slug:'vowelit', name:'Vowelit', repo:'pkkid/vowelit', section:'recent', website:'https://vowelit.pkarma.com',
    tagline:'A word game for Android, iOS and the web. Find words on a letter grid solo, or challenge your friends.',
    page:() => import('./pages/Vowelit.vue')},
  {slug:'claude-aitools', name:'Claude AITools', repo:'pkkid/claude-aitools', section:'recent',
    tagline:'A Claude Code mod that adds a slim bar showing usage and cost, plus task checklists and branch cleanup.'},
  {slug:'python-plexapi', name:'Python PlexAPI', repo:'pushingkarmaorg/python-plexapi', section:'recent', install:'pip install plexapi',
    tagline:'Python bindings for the Plex API. Navigate and manage your local or remote shared libraries.'},
  {slug:'django-dbbackup', name:'Django DBBackup', repo:'Archmonger/django-dbbackup', install:'pip install django-dbbackup',
    tagline:'Management commands to backup and restore project database to AmazonS3, Dropbox or Local Disk.'},
  {slug:'x11pygrid', name:'x11pygrid', repo:'pkkid/x11pygrid', install:'pip install x11pygrid',
    tagline:'Easily organize open windows by tiling and positioning them to make the best use of your desktop.',
    page:() => import('./pages/X11pygrid.vue')},
  {slug:'pkmeter', name:'PKMeter', repo:'pkkid/pkmeter',
    tagline:'Desktop system stats using Python3 and QT5.'},
  {slug:'algorithmx', name:'AlgorithmX', repo:'pkkid/python-algorithmx', section:'small',
    tagline:'Exact cover puzzles (sudoku, pentominoes and friends) solved with Knuth\'s Algorithm X.'},
  {slug:'link-manager', name:'Link Manager', repo:'pkkid/link-manager', section:'small',
    tagline:'Collection of scripts to help easily sync specific configuration files across all your Linux computers.'},
  {slug:'colorpecker', name:'Colorpecker', repo:'pkkid/colorpecker', section:'small',
    tagline:'A color picker written with PySide6 and QT.'},
  {slug:'chrome-tools', name:'Chrome Tools', repo:'pkkid/chrome-tools', section:'small',
    tagline:'Specify a custom new tab URL in Chrome.'},
  {slug:'django-searchquery', name:'Django Searchquery', repo:'pkkid/django-searchquery', section:'small',
    tagline:'Provides advanced search and filtering capabilities to structured data in Django models.'},
  {slug:'conky-pkmeter', name:'Conky PKMeter', repo:'pkkid/conky-pkmeter', section:'small',
    tagline:'Collection of scripts and a Conky configuration. Makes fetching data easy and results stored as json.'},
  {slug:'pushingkarma', name:'PushingKarma', repo:'pkkid/pushingkarma',
    tagline:'The Django, Django Ninja and Vue source for this website.'},
]
