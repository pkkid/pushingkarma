<template>
  <p class='lede'>
    Python PlexAPI started as a quick hack to see what was playing on my home network,
    and somehow grew into one of the most rewarding projects I have ever worked on.
  </p>
  <h2>Getting started</h2>
  <p>This is roughly the snippet that started it all, listing what is playing right now.</p>
  <CodeEditor :value='EXAMPLE' language='python' showlinenums readonly/>
  <h2>How it started</h2>
  <p>
    I was building a Conky script for my desktop and wanted it to show which videos were
    being played around the house. I went looking for a Python library to pull that out of
    my Plex server and came up empty. What I did notice was that the Plex web app was just
    calling XML endpoints on the server behind the scenes, so I wrote a few lines to read
    the current sessions and got my Conky script working.
  </p>
  <p>
    That should have been the end of it, but I kept wanting to see a little more
    information, and then a little more after that. Eventually I decided I might as well
    try to support everything the web app could do. There was no documentation at the time,
    so most of the library was built by watching the requests in my browser's developer
    tools, and implementing each endpoint by hand, one at a time. It took a very
    long time, and the library slowly grew into something much bigger than I ever planned.
  </p>
  <h2>The one button remote</h2>
  <p>
    The moment I realized this was more than a personal tool came from Reddit. A parent
    used the library and an Amazon Dash button to build a single button remote for their
    child, who has special needs and could not use a normal remote. Pressing the button
    turned on the TV and started a movie, and pressing it again started another one. I was
    in <a href='https://www.reddit.com/r/PleX/comments/4r9jd5/amazon_dash_button_python_randomizer_or_whatever/'>the
    thread</a> helping them get it working, and the post took off in a way I never
    expected. Seeing something I wrote make a real difference for a family was a pretty
    special feeling.
  </p>
  <h2>Growing beyond me</h2>
  <p>
    From there the project kept growing. A few other maintainers joined, and later the
    library was picked up by Home Assistant, which brought in even more users and
    contributors. We started a Discord, and one of our maintainers even turned out to be a
    Plex employee. Plex was kind enough to donate a server license so we could keep
    developing and testing against the real thing.
  </p>
  <p>
    I am honestly grateful to everyone who has contributed over the years. The project is
    far better than anything I could have built on my own, and these days the other
    maintainers deserve most of the credit for keeping it going.
  </p>
  <h2>Why it means so much to me</h2>
  <p>
    Every month or so I search for the package name just to see what people are building
    with it, and there is almost always something new and clever. Home automation, media
    dashboards, Discord bots, scripts to tidy up libraries. It is a great reminder that a
    small tool written to scratch your own itch can end up being useful to a lot of people.
  </p>
  <p>
    Plex now publishes <a href='https://developer.plex.tv'>official documentation</a> for its API, so there is plenty that could be
    cleaned up or improved. But the library has held up well, and I am happy to have been
    part of getting it off the ground.
  </p>
</template>

<script setup>
  import {CodeEditor} from '@/components'

  defineProps({project:{type:Object, required:true}})
  const EXAMPLE = [
    '# pip install plexapi',
    'from plexapi.server import PlexServer',
    '',
    '# Show what is playing on your Plex server',
    "plex = PlexServer('http://localhost:32400', token='your-token')",
    'for video in plex.sessions():',
    '    print(video.usernames, video.title)',
  ].join('\n')
</script>
