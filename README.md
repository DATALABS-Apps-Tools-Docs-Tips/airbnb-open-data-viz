# Data Visualization For Airbnb Open November 2016

## TODO

* Demand Index
    * ~~Add a timeline bar so users can scroll through time to see how things change~~ Use Animation Instead
    * ~~Add tooltip to each of the point~~
    * ~~Overlay a Google Map on top of the visualization~~
    * ~~Add dim country level color coding~~
    * Add a video to playback the demand index day-by-day
        * the Big label is not aligned correctly
        * ~~Country color coding~~
        * ~~Stop button doesn't seem to work~~
        * stress test more data
    * [WIP] Annotate time series by major events
        * ~~rote a event extractor to grab all events from excel file~~ see `event_extractor.py`
        * The dates are mostly old (2013 - 2015), and we don't have too many dates for 2016. Right now I just hack them so replace 2016 events using 2015 events.
        * Also need to fix the y-axis for the labels
