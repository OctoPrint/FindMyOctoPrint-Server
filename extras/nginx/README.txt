basic.conf
  Basic configuration. Fully forwards / to the server and uses built in (basic) website. Restricts
  access to /dump to localhost only.
custom_page.conf
  Custom configuration incl. SSL via LetsEncrypt and acmetool. /findmyoctoprint.js, /registry and /dump are
  forwarded to the server (the latter restricted to access from localhost). / is served from the static
  web root.