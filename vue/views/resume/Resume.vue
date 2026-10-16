<template>
  <div id='resume' class='lightbg'>
    <LayoutPaper>
      <!-- Resume Content -->
      <template #content>
        <BannerImage banner='/static/img/mtn-landscape.png' :y='0.4'/>
        <h1>Michael Shepanski
          <div class='subtext'>
            Boston, MA &nbsp;|&nbsp; {{phone}} &nbsp;|&nbsp; <a :href='`mailto:${email}`'>{{email}}</a><br/>
            <a href='https://linkedin.com/in/mshepanski/'>Linked In</a> &nbsp;|&nbsp;
            <a href='https://pushingkarma.com'>pushingkarma.com</a>
          </div>
        </h1>
        <p>Engineering and AI enablement leader with 24 years spanning software engineering, and product delivery.
          Proven track record of building high‐performing teams and shipping mission-critical SaaS platforms at cloud
          scale. Currently responsible for four product teams (16 engineers) with the help of one senior manager, and
          standing up three new India‐based teams (15 engineers) with local team leads and managers. Consistently
          recognized for technical leadership, product delivery, and mentorship - by both executives and direct reports.</p>

        <h2 id='recognition'>Recognition &amp; Impact</h2>
        <ul>
          <li>Joined as employee #15 and helped scale the organization to 700+ employees and $100M+ in annual
            recurring revenue, establishing the company as a market leader in cloud file services.</li>
          <li>Recognized for cross‐team leadership and deep ownership during key product deliverables, including
            the launch of the Nasuni Portal, Ransomware Protection, High-Availability/Non-Disruptive Upgrade, and
            Cloud Migrator.</li>
          <li>Praised by executive leadership for advocacy, high sense of urgency, and ability to build
            high‐performing, collaborative teams. Received Uni Award for outstanding employee achievements and
            contributions.</li>
          <li>Received Engineering Award for leadership, accountability, and technical execution.</li>
        </ul>

        <h2 id='experience'>Work Experience</h2>
        <div class='job'>
          <h3 id='nasuni'>Nasuni <span>Boston, MA &nbsp;|&nbsp; <a href='http://nasuni.com'>nasuni.com</a></span></h3>
          <div class='roles'>
            <div><em>Software Engineering Director</em> &nbsp;|&nbsp; <span>2021 - Present</span></div>
            <div><em>Senior Software Engineering Manager</em> &nbsp;|&nbsp; <span>2018 - 2021</span></div>
            <div><em>Software Engineering Manager</em> &nbsp;|&nbsp; <span>2016 - 2018</span></div>
            <div><em>Team Lead / Principal Software Engineer</em> &nbsp;|&nbsp; <span>2014 - 2016</span></div>
            <div><em>Senior Software Engineer</em> &nbsp;|&nbsp; <span>2011 - 2014</span></div>
            <div><em>Software Engineer</em> &nbsp;|&nbsp; <span>2009 - 2011</span></div>
          </div>
          <ul>
            <li>Mentored and developed engineering talent, successfully coaching key individual contributors into
              management and leadership roles to support organizational scaling.</li>
            <li>Spearheaded the design and deployment of an enterprise test analytics platform integrated with
              Jenkins, Zephyr, and Jira, tracking millions of CI/CD test results to optimize quality metrics and
              engineering efficiency (built with Vue.js, Python, Django-Ninja, and SQLite).</li>
            <li>Championed organization-wide AI adoption initiatives, establishing best practices, driving technical
              readiness, and maximizing developer productivity and innovation ROI.</li>
            <li>Lead the team migrating the product UI from legacy Django jQuery to a more modern SaaS architecture
              leveraging Python FastAPI, React, and Typescript.</li>
            <li>Responsible for Filer product UI and backend code consisting of Python, Django and Postgres, C, C++
              and Javascript. Added multiple new features such a filesystem browser, SNMP tracking, and directory
              level settings that synchronize across multiple customer installs.</li>
            <li>Design, implement, and maintain Network Operations Center (NOC) tracking customer usage and
              providing a central API point for all customer installs to coordinate communications. Written primarily
              in Python and Django. System heavily takes advantage of the AWS infrastructure including 25 EC2
              instances, Postgres RDS, Simple Queue Service, Lambda and Redis ElastiCache. Currently tracks and
              analyses 200 million metrics across several thousand product installs to provide real-time updates to
              our internal services.</li>
            <li>Develop Nasuni Management Console (NMC) allowing customers to manage and configure multiple
              products from a single endpoint. System maintained state about each Filer and communicated through
              the Azure Service Bus.</li>
          </ul>
        </div>
        <div class='job'>
          <h3 id='hitachi'>Hitachi Data Systems - HCP <span>Boston, MA</span></h3>
          <div class='roles'>
            <div><em>Software Engineer</em> &nbsp;|&nbsp; <span>2006 - 2009</span></div>
          </div>
          <ul>
            <li>Responsible for maintaining Python based installer of our main HCAP product. Add new features and
              debug any problems that arose.</li>
            <li>Lead technical efforts of the test automation group to write and run all automation tests written in
              Python, Java and Perl provided by the QA team. Responsibilities included code delegation, code review,
              and reports for oversea hires.</li>
            <li>Maintained and extended abilities of an in-house test scheduler written using Python, PHP and
              PostgreSQL. Created results management application to track and organize thousands of tests
              continuously running 24/7.</li>
          </ul>
        </div>
        <div class='job'>
          <h3 id='emc'>EMC Corporation - Centera <span>Boston, MA</span></h3>
          <div class='roles'>
            <div><em>Software Engineer</em> &nbsp;|&nbsp; <span>2004 - 2006</span></div>
          </div>
          <ul>
            <li>Create Java based Test Framework. One of three engineers building a Java based automated test
              framework providing enhancements and adding new features such as automated logging and graphing.</li>
            <li>Design, implement, and maintain PHP/MySQL data mining infrastructure. Proposed a plan to create data
              mining system after seeing a lack of result analysis from existing tests. Created infrastructure with
              ability to compute, analyze and graph test results directly from a test run. System provided complete
              health reports for over 300 test servers running in the lab. Appointed to lead a four man group to
              enhance and develop more features into the system which is now used by three international groups
              within the department.</li>
          </ul>
        </div>
        <div class='job'>
          <h3 id='borgwarner'>BorgWarner Morse TEC <span>Ithaca, NY</span></h3>
          <div class='roles'>
            <div><em>Software Engineer</em> &nbsp;|&nbsp; <span>2002 - 2004</span></div>
          </div>
          <ul>
            <li>Automate process to measure sound intensity across automotive engines.</li>
            <li>Designed and coded extensive VB.Net application to physically control microphone across a 2D array of
              user defined data positions while recording and visually graphing sound intensity.</li>
          </ul>
        </div>

        <h2 id='projects'>Personal Projects</h2>
        <p><a href='https://github.com/pkkid'>https://github.com/pkkid</a></p>
        <ul>
          <li><strong>Dalica</strong> - Photo management application largely delivered with the use of AI leveraging
            parallel subagents and a very detailed implementation plan and milestones. Was mostly a learning exercise
            in how to effectively build larger applications with frontier AI models.</li>
          <li><strong>Python PlexAPI</strong> - Python bindings for the Plex Media Server with a goal to match
            capabilities of the official Plex Web Client. Became successful in the open source community.</li>
          <li><strong>Django SearchQuery</strong> - Advanced yet user-friendly query search capabilities for Django
            models, currently serving as the dedicated search layer for the Nasuni Management Console.</li>
          <li><strong>Django DBBackup</strong> - Provider-recommended DB backup and restore strategies for Django
            databases. This community-maintained project is now a part of the Jazz Band organization on Github.</li>
        </ul>

        <h2 id='education'>Education</h2>
        <div class='roles'>
          <div><em>Northeastern University &nbsp;|&nbsp; MS in Software Engineering</em> &nbsp;|&nbsp; <span>2012</span></div>
          <div><em>Rochester Institute of Technology &nbsp;|&nbsp; Bachelor in Computer Engineering</em> &nbsp;|&nbsp; <span>2004</span></div>
        </div>
      </template>
      <!-- Table of Contents & Controls -->
      <template #controls>
        <NotesToc title='Michael Shepanski' :headings='headings'/>
        <h2>Resume Options</h2>
        <div class='submenu'>
          <div><a class='h1' :href='PDFURL' :download='FILENAME'>Download PDF</a></div>
          <div><a class='h1' href='#' @click.prevent='print'>Print Resume</a></div>
        </div>
      </template>
    </LayoutPaper>
  </div>
</template>

<script setup>
  import {onBeforeMount, onMounted, ref} from 'vue'
  import {NotesToc} from '@/views/notes'
  import {BannerImage, LayoutPaper} from '@/components'
  import {utils} from '@/utils'

  const PDFURL = '/static/files/resume.pdf'
  const FILENAME = 'Michael Shepanski Resume.pdf'
  const email = atob('bWljaGFlbC5zaGVwYW5za2lAZ21haWwuY29t')
  const phone = atob('KDU4NSkgMzU1LTU0OTY=')
  const headings = ref(null)

  onBeforeMount(function() { utils.setNavPosition('left') })

  // On Mounted
  // Build the table of contents from the section and job headings
  onMounted(function() {
    var elems = document.querySelectorAll('#resume article h2[id], #resume article h3[id]')
    headings.value = Array.from(elems).map(function(elem) {
      return {id:`#${elem.id}`, text:elem.childNodes[0].textContent.trim(), tag:elem.tagName.toLowerCase()}
    })
  })

  // Print
  // Print the resume page; nav, footer and controls are hidden by the print styles
  const print = () => window.print()
</script>

<style>
  #resume {
    article {
      &:has(#bannerimage) h1 { margin-top: 170px; }
      h1 {
        text-align: center;
        &:after { margin: 0px auto; }
        .subtext { font-size: 13px; margin-top: 5px; }
      }
      h3 span {
        color: var(--lightbg-fg4);
        font-family: var(--fontfamily-article);
        font-size: 13px;
        font-weight: 400;
        margin-left: 10px;
      }
      .job { margin-bottom: 25px; }
      .roles {
        font-size: 14px;
        margin-bottom: 10px;
        span { color: var(--lightbg-fg4); white-space: nowrap; }
      }
    }
  }

  @media print {
    #resume article {
      font-size: 12px;
      line-height: 1.5;
      h1 { margin-bottom: 15px; }
      &:has(#bannerimage) h1 { margin-top: 0px; }
      h2 { break-after: avoid; margin-top: 20px; }
      h3 { break-after: avoid; }
      li { break-inside: avoid; }
      .job { margin-bottom: 15px; }
      .roles { font-size: 12px; }
    }
  }
</style>
