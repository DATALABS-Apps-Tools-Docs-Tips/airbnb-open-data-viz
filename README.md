# Airbnb Open November 2016 - Interactive Demand Data Visualization

## Introduction

The following data app is built for 2016 Airbnb Open using [Bokeh] and [Heroku]. The idea is to showcase, to hosts and guests at the event, how global Airbnb truly is. The app consists of a world map which showcase the demand (measured by number of searches, normalized) across different regions around the world, as well as a time series visualization where users can pick their home market to learn more about the cyclical nature of our business. Below is a screenshot of the app, and the entire app can be accessed from this [URL].

![alt text][screenshot]

## Organization

The main app is organized under `main.py`, where all the mapping of data to visual elements are done. `data.py` consists of all the data wrangling tasks to tidy the data into a shape we want for the visualization.

The `data` folder consists of all the snapshot of data that powers the app, the data are queried from our own data warehouse via airpy, but to reduce the dependencies, I simply queried the data once and save them in various .csv files. This is not the most efficient way to organize an app, since each request will need to load up all the data upfront.

The `templates` directory consists of all the htmls, mostly text describing what each of the visualization does.

The `static` folder consists of static resources like Airbnb belo logo.

`server_lifecycle.py` is intended to be executed before the app starts, I used it to load all the data upfront, but this doesn't work well with Heroku, so I just left them out for now.

`Procfile`, `runtime.txt`, and `requirements.txt` are required for Heroku to know so it can properly deploy the app, for more details, see the next section.

## Heroku Deployment

The prerequiste is to sign up for a Heroku account. At the prompt, login to heroku using `heroku login`, and enter your email address and password.

```bash
# create a project name airbnb-open-data-viz
heroku create airbnb-open-data-viz

# For Heroku to know how to deploy your app, need to supply a Procfile & requirements.txt file
touch Procfile
pip freeze > requirements.txt

# Git add and commit your files
git add 
git commit 

# Make sure that Heroku knows your app is a Python app
heroku buildpacks:set heroku/python

# Test your app locally before pushing to Heroku
heroku local web

# Push the app to heroku
git push heroku master

# Check out tail of the logs to monitor the app
heroku logs -t
```

## Credits

This app is not possible without the support of the underlying data created by the pricing team, particularly Milan Shen. For the interested, one can access this data in `pricing.local_demand_index`, some of the relevant pipelines are available in the [data repo], and also check out the [presentation]. Special thanks to Martin, Vaughn, Theresa for giving me feedbacks during the few weekends of my development times.

## Disclaimer

I spent a few weekends hacking and learning how to use Bokeh and Heroku, and this work is largely experimental, and are in no way production ready. In retrospect, using a combination of Flask and d3.js is probably a better choice, since these tools have better db supports and customization. Perhaps we can do that in the next iteration of the app. I hope this example can inspire people to learn bokeh, but more broadly building data visualization on the web in general. 

[Bokeh]:http://bokeh.pydata.org/en/latest/
[Heroku]:https://dashboard.heroku.com/
[URL]:https://airbnb-open-data-viz.herokuapp.com/
[screenshot]:https://git.musta.ch/robert-chang/airbnb-open-data-viz/blob/master/static/images/airbnb_open_data_viz.png
[data repo]:https://git.musta.ch/airbnb/data/blob/e742d89b41b0eb00bcd97f79cced22fd466af54a/airflow/pricing/demand_index_pipeline.py
[presentation]:https://docs.google.com/presentation/d/1GBEBOLc5aGooqT4f_zgE7WIPLbD0PFJjCtbPpsSa2nc/edit#slide=id.g104fabfb57_0_5