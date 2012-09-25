@echo off
cd %cd%\tutorial
scrapy crawl dmoz -o items.json -t json
