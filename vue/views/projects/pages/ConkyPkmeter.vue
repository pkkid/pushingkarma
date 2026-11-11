<template>
  <div id='conkypkmeter'>
    <p class='lede'>
      Conky PKMeter is the sidebar that runs on every one of my computers. It is a Conky
      configuration written entirely in Lua, and it is the latest stop in a long habit of
      wanting to see exactly what my system is doing.
    </p>
    <h2>Getting started</h2>
    <p>On Ubuntu or Debian:</p>
    <CodeEditor :value='INSTALL' language='bash' showlinenums readonly/>
    <h2>Why I need to see it</h2>
    <p>
      I have always loved being able to understand what my computer is doing at a
      fundamental level. If I am sitting at my desk and cannot see the little bars showing
      how hard the processor is working and how much memory is free, I do not feel like I
      fully understand what I am doing. It is probably a slightly weird way to think about
      computers, but it is how my brain works. I need to know what the system I am using is
      up to.
    </p>
    <p>
      Because of that, I have always gravitated toward tools like Rainmeter and Conky that
      put those stats right on the desktop.
    </p>
    <h2>Before Conky, there was PKMeter</h2>
    <p>
      My first attempt at this was <a href='https://github.com/pkkid/pkmeter'>PKMeter</a>,
      a cross-platform desktop stats app I wrote in Python with Qt5. It had a small plugin
      system for adding new meters and simple HTML templates for laying them out, and for
      the most part it worked pretty well. But I was really the only one using it, and it
      never caught on. Over the years, keeping it running and its libraries up to date just
      was not worth the time, so I let it go and started using Conky much more seriously
      instead.
    </p>
    <h2>One big Lua app</h2>
    <p>
      I started with some basic Conky scripts like everyone else. What makes Conky
      interesting is that it can run Lua to draw charts and graphics. Most of the Conky
      community uses Lua for a widget here and there, but builds the actual layout with
      Conky's own configuration syntax.
    </p>
    <p>
      I wanted to try something different and make the whole thing one large Lua app. Conky
      still gathers the stats on the back end, but everything on the front end is mine to
      control. That opened up a lot: right click menus, widgets that animate at 15 frames a
      second while others update once a second, choosing the order of the widgets, turning
      them on or off, and generally having much more say in what shows up on my desktop. It
      also let me make it work on any system without the user having to configure anything
      first.
    </p>
    <h2>Where it is now</h2>
    <p>
      This has become my main sidebar on all of my computers. I have never really
      advertised it, so it has not taken off with other people, but it has been working
      really well for me.
    </p>
    <p>
      The biggest change lately has been AI. Adding a new widget used to take me thirty to
      forty five minutes of fiddling. Now if I am missing something or want to show
      something new, I describe it to an AI assistant and three or four minutes later it is
      on my sidebar. It has made tinkering with this project more fun than ever.
    </p>
  </div>
</template>

<script setup>
  import {CodeEditor} from '@/components'

  defineProps({project:{type:Object, required:true}})
  const INSTALL = [
    'sudo apt install conky-all lua-socket lua-sec playerctl curl unzip',
    'git clone https://github.com/pkkid/conky-pkmeter.git',
    'cd conky-pkmeter',
    'conky -c conkyrc',
  ].join('\n')
</script>

