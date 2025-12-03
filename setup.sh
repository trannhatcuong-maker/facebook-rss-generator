#!/bin/bash
# Fix dependencies for facebook-scraper
pip install --upgrade pip
pip install facebook-scraper==0.2.63
pip install lxml html5lib beautifulsoup4
pip install feedgen pytz
