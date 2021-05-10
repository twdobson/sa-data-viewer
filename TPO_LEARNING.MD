# Microblog learnings applicable to TPO

# resources
- 'professional' dashboard example => https://towardsdatascience.com/create-a-professional-dasbhoard-with-dash-and-css-bootstrap-e1829e238fc5 

# High level stuff
- Flask application factory design pattern (with all it's benefits)
- 12-factor app development (What does this mean for python?)


## model
- Unique constraint (in column definition)
- Index (in column definition) - https://en.wikipedia.org/wiki/Database_index
- Mixin classes? e.g. for login
- Unit testing (via model functions) - sort of...

## Database migration

## Docker image to use?
- https://pythonspeed.com/articles/base-image-python-docker-images/
- Avoid using root user. In docker
- Docker compose (spin up db, as persisted volume and then separate app)
- Consider other security vulnerabilities
- use docker BD in development


# Database learnings
- db.Create_all(), avoids duplication of model specification (see initial ingest of data)
  - Follow this up with a bulk insert


# coding principles
- make code easier to change / update using wrapped functions
- e.g. new optimisations are found
- Pandas read_sql is really slow and memory inefficient -- https://towardsdatascience.com/optimizing-pandas-read-sql-for-postgres-f31cd7f707ab

## Use make file more
- Ease of setup
- Standardise the flow of commands

## multi page dash app
https://medium.com/@olegkomarov_77860/how-to-embed-a-dash-app-into-an-existing-flask-app-ea05d7a2210b   
https://community.plotly.com/t/embed-multipage-dash-app-in-existing-flask-app-with-dash-bootstrap-components/34773


## replicating what I am trying to do
https://towardsdatascience.com/embed-multiple-dash-apps-in-flask-with-microsoft-authenticatio-44b734f74532
https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
https://github.com/facultyai/dash-bootstrap-components
https://medium.com/@olegkomarov_77860/how-to-embed-a-dash-app-into-an-existing-flask-app-ea05d7a2210b
