<template>
  <p class='lede'>
    Puzzle a Day started with a little wooden calendar puzzle and turned into one of my
    favorite places to tinker with code, algorithms and, lately, AI.
  </p>
  <h2>Getting started</h2>
  <p>Solve any date from the command line with either the Python or the Rust solver.</p>
  <CodeEditor :value='EXAMPLE' language='bash' showlinenums readonly/>
  <h2>How it started</h2>
  <p>
    I have always enjoyed little side projects like this as a hobby, where the whole point
    is finding an efficient way to solve a problem. So after I bought Dragonfjord's
    <a href='https://www.dragonfjord.com/product/a-puzzle-a-day/'>A Puzzle a Day</a>, a
    board where you fit eight pieces around the current month and day, I realized I
    wanted to write a script to solve it for me. Some days are easy, some days are really
    hard, and writing code to find the answer just sounded like fun.
  </p>
  <p>
    My first attempt was a brute force solution in Python. It worked, but it would run on
    my computer for hours, sometimes overnight, to get through the year. It was not
    anywhere close to efficient.
  </p>
  <h2>Discovering Algorithm X</h2>
  <p>
    Rather than switch languages, I wanted to see how far I could get while staying in
    Python, which is where I am most comfortable. That search led me to Donald Knuth's
    <a href='https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X'>Algorithm X</a> and his
    paper on <a href='https://arxiv.org/abs/cs/0011047'>Dancing Links</a>, which treat
    puzzles like this as an exact cover problem. With help from Ali Assaf's write up and
    implementation, I got it working in Python, and the run time dropped from hours down
    to several minutes. Still not fast, but a huge improvement, and I had a blast writing
    it.
  </p>
  <h2>Laser cutting new puzzles</h2>
  <p>
    From there I started experimenting with my laser cutter, cutting out my own boards and
    trying new piece shapes to fill them. The catch is that a good piece set needs a
    solution for every single day of the year. My solver turned out to be perfect for
    this, since I could design a set, run it against the whole calendar, and immediately
    see whether it worked.
  </p>
  <h2>What makes a puzzle hard</h2>
  <p>
    That sent me down another rabbit hole: what makes one of these puzzles harder than
    another? I assumed a day with fewer solutions would be harder. It turns out that is
    not the case at all. Days with very few solutions tend to be easier, because pieces
    get forced into certain positions. A person can look at the board, spot a corner
    where only one piece fits, and the rest falls into place from there.
  </p>
  <p>
    Too many solutions makes a puzzle easy, and too few makes it easy in a different way.
    The hard puzzles live somewhere in the middle. Using that, I found a few new piece
    sets, cut them out and gave them to friends, which was a really fun experiment.
  </p>
  <p>
    I also wrote up an
    <a href='https://www.reddit.com/r/puzzles/comments/t9uejy/analysis_of_a_puzzle_a_day/'>analysis
    of A Puzzle a Day</a> and posted it on Reddit. Digging into the numbers behind the
    puzzle was really interesting, and if you enjoy this kind of thing, it is a fun read.
  </p>
  <h2>Rust, AI and going way too fast</h2>
  <p>
    Just recently I came back to the project with AI and asked it to port my solver to
    Rust, mostly to see how fast it could get. It came out around a hundred times faster
    than my Python version, which I more or less expected. Then I let it off the leash
    and asked it to build the fastest solver it could, and what it came up with honestly
    blew me away. It packs the whole board into a single 64 bit integer, prunes any
    pocket of empty squares the remaining pieces could never fill, and solves every date
    of the year together instead of one at a time.
  </p>
  <ul>
    <li>Solving every day of 2025 on the original board took my Python solver about two
      and a half minutes. The fastest Rust solver does it in 0.076 seconds on one core.</li>
    <li>On a much harder board, Python needed close to an hour for the year. Rust does it
      in under four seconds on one core, and under half a second using all of them.</li>
  </ul>
  <p>
    That is the kind of speed I never could have dreamed of with my Python code, and it
    opens up a lot. AI can now help search for brand new piece sets that solve every day,
    and even rate how hard they are with a simulated solver that plays the way a person
    does.
  </p>
  <h2>Running in the browser</h2>
  <p>
    Having a Rust version also means it can be compiled to WebAssembly. The repo now
    includes a playable web version where you can drag, rotate and flip the pieces
    yourself, pick any date, and press Solve to watch a solution slide into place. The
    whole solver is about 100 KB and finds a solution in a millisecond or two, right in
    the browser. That was never something I could have done with the Python version.
  </p>
  <p>
    More than anything, this project has become a great learning bed for me, and just a
    fun place to tool around with code and different ways of solving the same problem.
  </p>
</template>

<script setup>
  import {CodeEditor} from '@/components'

  defineProps({project:{type:Object, required:true}})
  const EXAMPLE = [
    'git clone https://github.com/pkkid/puzzle-a-day.git',
    'cd puzzle-a-day',
    '',
    '# The original Python solver',
    'python3 python/puzzle-a-day.py --date=2025-05-29',
    '',
    '# The Rust solver, about a hundred times faster',
    'cd rust && cargo build --release',
    './target/release/puzzle-a-day --date=2025-05-29',
  ].join('\n')
</script>
