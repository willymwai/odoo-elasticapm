#!/bin/bash

SECRET32="$(dd if=/dev/urandom count=1 2> /dev/null | uuencode -m - | sed -ne 2p | cut -c-32)"
SECRETPW="$(dd if=/dev/urandom count=1 2> /dev/null | uuencode -m - | sed -ne 2p | cut -c-10)"

if [ ! -f kibana.yml ]; then
  cat kibana.yml.example | sed "s!__SECRET32CHARS__!$SECRET32!" > kibana.yml
fi

if [ ! -f .env ]; then
  cat .env.example | sed "s!__SECRETPW__!$SECRETPW!" > .env
fi
