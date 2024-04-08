#!/bin/bash
# Author: sh1mu7
# Date: 2024-02-06
# Description: Django deployment automation.

# Prompt for service name
# shellcheck disable=SC2162
read -p "Enter service name: " NAME

# Prompt for domain name
read -p "Enter domain name: " DOMAIN

# Prompt for project directory
read -p "Enter project directory: " PROJECT_DIR

# Check if arguments are provided
if [ -z "$NAME" ] || [ -z "$DOMAIN" ] || [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <service_name> <domain_name> <project_directory>"
    exit 1
fi

# Remove existing service and socket files if they exist
if [ -f "/etc/systemd/system/$NAME.service" ]; then
    rm "/etc/systemd/system/$NAME.service"
fi

if [ -f "/etc/systemd/system/$NAME.socket" ]; then
    rm -rf  "/etc/systemd/system/$NAME.socket"
fi

# Remove existing Nginx configuration file if it exists
if [ -f "/etc/nginx/sites-available/$DOMAIN" ]; then
    rm -rf "/etc/nginx/sites-available/$DOMAIN"
fi



systemctl daemon-reload

# Create systemd service file for project
cat <<EOL > "/etc/systemd/system/$NAME.service"
[Unit]
Description=$NAME daemon
Requires=${NAME}.socket
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn Config.wsgi:application -w 2 --bind unix:/run/${NAME}.sock --access-logfile -

[Install]
WantedBy=multi-user.target
EOL

# Create systemd socket file for Project
cat <<EOL > "/etc/systemd/system/$NAME.socket"
[Unit]
Description=$NAME socket

[Socket]
ListenStream=/run/${NAME}.sock

[Install]
WantedBy=sockets.target
EOL

# Create Nginx server block
cat <<EOL > "/etc/nginx/sites-available/$DOMAIN"
server {
    listen 80;
    server_name $DOMAIN;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        root $PROJECT_DIR;
    }

    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/${NAME}.sock;
    }

     client_max_body_size 20M; # Set maximum request body size to 20 megabytes

     # Enable gzip compression
     gzip on;
     gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
     # Cache settings
#     proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;

}
EOL

# Create a symbolic link for Nginx server block only if it doesn't already exist
if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    ln -s "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
fi


# Reload systemd and Nginx
systemctl daemon-reload
systemctl restart "$NAME"
systemctl reload nginx

# Install and configure Let's Encrypt SSL certificate
certbot --nginx -d "$DOMAIN"

systemctl daemon-reload
systemctl restart "$NAME"
systemctl reload nginx

echo "Deployment complete for $NAME on $DOMAIN with project directory $PROJECT_DIR!"



















































































