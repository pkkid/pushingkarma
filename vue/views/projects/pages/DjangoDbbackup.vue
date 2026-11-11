<template>
  <p class='lede'>
    Django DBBackup is another tool I built for myself, written so other people could use
    it too. To my surprise, they did.
  </p>
  <h2>Getting started</h2>
  <p>
    Add <code>dbbackup</code> to your installed apps, point it at a storage, and you have
    backup and restore commands that use your database's own tools.
  </p>
  <CodeEditor :value='EXAMPLE' language='python' showlinenums readonly/>
  <h2>How it started</h2>
  <p>
    When I first went looking at backup tools for Django, I liked that they all shared a
    common approach. They dumped the database to JSON using Django's own serializers,
    which works with any database and is easy to understand. The trouble was that it did
    not hold up well as a database got really large. The dumps were slow, they were big,
    and they did not compress nearly as well as they could.
  </p>
  <p>
    What I really wanted was something built into Django that backed up the database the
    way the database itself recommends. Every major database ships with its own backup
    tools, and they are almost always faster and produce much smaller files than a JSON
    dump. So I wrote a few management commands that called those tools directly, starting
    with just MySQL and PostgreSQL, the databases I was using at the time.
  </p>
  <p>
    Once that was working, it seemed silly to stop there. If it was useful for my
    databases, it would probably be useful for other people's too, so I filled in support
    for the rest, packaged it up and put it online. It caught on more than I expected, and
    people seemed to like the idea of doing backups the native way without leaving Django.
  </p>
  <h2>Taking on a life of its own</h2>
  <p>
    As the project grew, it was taken in by <a href='https://jazzband.co'>Jazzband</a>, a
    collaborative community of developers who share the work of maintaining Django apps
    and other Python projects. Having a whole group of people looking after it made it far
    better than it would have been with just me. Later, the current lead maintainer,
    <a href='https://github.com/Archmonger'>Archmonger</a>, moved it to their own GitHub
    account, where it is still actively maintained today.
  </p>
  <p>
    It has been fun to watch this one grow, get pulled in different directions by the
    Django community, and end up somewhere I never would have taken it on my own. I am
    grateful to everyone who has helped maintain it along the way. In the end it is just
    another tool I built to solve my own problem, but I tried to build it so other people
    could use it, and finding out that they did is always rewarding.
  </p>
  <p>
    The <a href='https://archmonger.github.io/django-dbbackup/'>official documentation</a>
    covers every supported database and storage, plus encryption and compression options.
  </p>
</template>

<script setup>
  import {CodeEditor} from '@/components'

  defineProps({project:{type:Object, required:true}})
  const EXAMPLE = [
    '# pip install django-dbbackup',
    "INSTALLED_APPS += ['dbbackup']",
    'STORAGES = {',
    '    # ...your existing default and staticfiles storages',
    "    'dbbackup': {",
    "        'BACKEND': 'django.core.files.storage.FileSystemStorage',",
    "        'OPTIONS': {'location': '/var/backups'},",
    '    },',
    '}',
    '',
    '# Then from the command line',
    '# python manage.py dbbackup --compress',
    '# python manage.py dbrestore',
  ].join('\n')
</script>
