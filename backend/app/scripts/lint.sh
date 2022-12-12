#!/usr/bin/env bash

set -x

isort --check-only app
black app --check
flake8