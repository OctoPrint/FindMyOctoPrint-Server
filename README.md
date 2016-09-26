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
$ findmyoctoprint --help
Usage: findmyoctoprint-script.py [OPTIONS]

Options:
  --address TEXT  The host under which to run
  --port INTEGER  The port under which to run
  --cors TEXT     Setting for Allowed-Origin-Host CORS header
  --help          Show this message and exit.
```

### Example

```
$ findmyoctoprint --port 5000 --address 127.0.0.1 --cors "http://example.com"
2016-09-26 17:22:21,555 - findmyoctoprint.server - INFO - Starting Find My OctoPrint server...
2016-09-26 17:22:21,628 - findmyoctoprint.server - INFO - Binding to 127.0.0.1:5000
```

## Setup Nginx

```
sudo apt-get install nginx
```

Basic configuration:

```
server {
        listen 80;

        server_name example.com;
        server_tokens off;

        gzip on;
        gzip_vary on;
        gzip_min_length 1000;
        gzip_comp_level 5;
        gzip_types application/json text/css application/x-javascript application/javascript;

        keepalive_timeout 65;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        location / {
                proxy_pass http://127.0.0.1:5000/;
                proxy_set_header        X-Real-IP       $remote_addr;
                proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /dump {
                # restrict to localhost
                allow 127.0.0.0/8;
                deny all;
                proxy_pass http://127.0.0.1:5000/dump;
        }

        location /.well-known/acme-challenge/ {
                default_type "text/plain";
                root /usr/share/nginx/html/acme;
        }
}
```

Configuration incl. LetsEncrypt using [acmetool](https://hlandau.github.io/acme/) with custom HTML in `/var/www/html`:

```
server {
        listen 80;
        listen 443 ssl;

        server_name example.com;
        server_tokens off;

        gzip on;
        gzip_vary on;
        gzip_min_length 1000;
        gzip_comp_level 5;
        gzip_types application/json text/css application/x-javascript application/javascript;

        keepalive_timeout 65;

        ssl_certificate /var/lib/acme/live/example.com/fullchain;
        ssl_certificate_key /var/lib/acme/live/example.com/privkey;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers HIGH:!aNULL:!MD5;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        location /findmyoctoprint.js {
                proxy_pass http://127.0.0.1:5000/findmyoctoprint.js;
        }

        location /registry {
                proxy_pass http://127.0.0.1:5000/registry;
                proxy_set_header        X-Real-IP       $remote_addr;
                proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /dump {
                # restrict to localhost
                allow 127.0.0.0/8;
                deny all;
                proxy_pass http://127.0.0.1:5000/dump;
        }

        location /.well-known/acme-challenge/ {
                default_type "text/plain";
                root /usr/share/nginx/html/acme;
        }
}
```
