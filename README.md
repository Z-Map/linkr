# Linkr app
## URL Shortener

# Description

This a technical exercice with the goal of creating an url shortener service in
Python.

The design of the project is the following :

Two service are deployed
- the "app" on app.mydomain.com
- a redirecter service on mydomain.com/[...]

Where the `mydomain.com/` redirect to app.mydomain.com/.
The idea behind it is to create url redirection through app.mydomain.com and
keep the short url with url index as short string to have the shortest possible
url able to redirect trafic.

# Install and run

You can install the project using the following command (you need poetry tool) :
```zsh
poetry install
```