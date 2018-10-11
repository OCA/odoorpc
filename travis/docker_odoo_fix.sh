#!/bin/sh
# Upgrade postgresql-client to get a recent version of pg_dump
# (required by Odoo 12 to get backup methods working on PostgreSQL 10)
if [ "$ODOO_VERSION" = "12.0" ]; then
  apt-get update
  apt-get install -y gnupg2
  curl -qq https://www.postgresql.org/media/keys/ACCC4CF8.asc -o - | apt-key add -
  echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list
  apt-get update
  apt-get upgrade -y -t stretch-pgdg postgresql-client-10
fi
