# Parsing Iowa City Police Log

This repo currently (12/2015) contains two Python scripts for acessing, downloading, parsing and storing the Iowa City Police department's activity log. 

The script `build.py` is modified with the user's desired data base location, Google Maps API key and the dates of data that currently exist on the website to be scraped. It is intended to be run first. It works by accessing the log and then parsing each row of the table using Beautiful Soup. A `sqlite` database with the table `events` is created and contains the data elements

* `dispatchNumber`: Dispatch number
* `incNumber`: Incidence number
* `month`, `day`, `year`: Event month, day and year
* `hour`, `minute`: Event time 
* `address`, `apt`: Reported event location and optional apartment
* `lat`, `lng`: Google Maps API geocoded location for `address`
* `activity`: Nature of the call
* `disposition`: What was the resolution of the call
* `note`: Optional note field with additional information

The second script `update.py` is intended to be run daily to update the `events` table with _yesterday's_ data. I would run it as a `cron` job daily at noon. Note that the log is delayed by several hours.  
