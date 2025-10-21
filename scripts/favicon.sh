#!/bin/bash

# Regenerate favicon.ico from favicon.svg

cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." || exit

bunx svg-to-ico assets/images/favicon.svg static/favicon.ico
