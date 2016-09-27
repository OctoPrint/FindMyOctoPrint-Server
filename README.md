# FindMyOctoPrint-Server

## Installation

```
git clone https://github.com/foosel/FindMyOctoPrint-Server
cd FindMyOctoPrint-Server
virtualenv venv
source venv/bin/activate
pip install .
```

## Usage

```
(venv) $ findmyoctoprint --help
Usage: findmyoctoprint-script.py [OPTIONS]

Options:
  --address TEXT  The host under which to run
  --port INTEGER  The port under which to run
  --cors TEXT     Setting for Allowed-Origin-Host CORS header
  --help          Show this message and exit.
```

### Example

```
(venv) $ findmyoctoprint --port 5000 --address 127.0.0.1 --cors "http://example.com"
2016-09-26 17:22:21,555 - findmyoctoprint.server - INFO - Starting Find My OctoPrint server...
2016-09-26 17:22:21,628 - findmyoctoprint.server - INFO - Binding to 127.0.0.1:5000
```

### System service

Init script and systemd service file can be found in ``extras/service``.
 
Be sure to adjust ``/etc/default/findmyoctoprint`` (when using sysvinit)
or ``/etc/systemd/service/findmyoctoprint.service`` (when using systemd)
to match your setup with regards to server executable path, binded address,
port and allowed CORS host.

## Setup Nginx

Configuration samples can be found in ``extra/nginx``.

When accessing the registry via https from a http page (e.g.
you are accessing the page on ``http://example.com`` and it uses
``https://example.com/registry`` as endpoint for querying the registry),
make sure to set the CORS allowed header via the ``--cors`` command
line argument on server start to allow access to the registry from
``http://example.com``:

```
$ findmyoctoprint --port 5000 --address 127.0.0.1 --cors "http://example.com"
```

## Sample page & client usage

The following sample page is very similar to the included stock ``index.html`` but
shows how to configure the included ``findmyoctoprint.js`` module.

The server here is assumed as running under both ``http://example.com``
and ``https://example.com`` - adjust accordingly.

The endpoint for querying the server's registry is set via ``findmyoctoprint.options.queryUrl``.

``findmyoctoprint.discover`` returns a promise - individual discovered
entries are provided as progress, the promise is finally resolved with a full
set of all discovered entries, as an object mapping from found UUID to discovered entry.

Entries consist of the fields ``url``, ``name`` and ``uuid``.

```
<html>
    <head>
        <title>Find my OctoPrint</title>

        <!-- Enable responsive viewport -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
        <script type="text/javascript" src="https://example.com/findmyoctoprint.js"></script>
        <script type="text/javascript">
            $(function() {
                findmyoctoprint.options.queryUrl = "https://example.com/registry";
            
                var performDiscovery = function() {
                    var discovered = $("#discovered");
                    discovered.empty();

                    findmyoctoprint.discover()
                            .progress(function(entry) {
                                console.log("Found entry:", entry);
                                discovered.append($("<li><a href=\"" + entry.url + "\" target=\"_blank\" title=\"" + entry.uuid + "\">" + entry.name + "</a></li>"));
                            })
                            .done(function(entries) {
                                console.log("Discovery done, entries:", entries);
                            })
                            .fail(function() {
                                console.log("Discovery failed");
                            });
                };

                $("#rescan").click(performDiscovery);
                performDiscovery();
            });
        </script>
    </head>
    <body>
        <h1>Find my OctoPrint</h1>

        <ul id="discovered"></ul>

        <a id="rescan" href="javascript:void(0)">Rescan...</a>
    </body>
</html>
```
