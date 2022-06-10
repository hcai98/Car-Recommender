import logging.config
from typing import Union

import sqlite3
import sqlalchemy.exc
from flask import Flask, jsonify, render_template, request, Response
from werkzeug.exceptions import BadRequestKeyError

# For setting up the Flask-SQLAlchemy database session
from src.database.create_db import Cars # type: ignore
from src.database.add_cars import CarManager  # type: ignore
from src.flaskapp.flask_models import Form  # type: ignore
from src.flaskapp.recommend import validate_input, get_recommendation  # type: ignore

# Initialize the Flask application
app = Flask(__name__,
            template_folder='app/templates',
            static_folder='app/static')

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config['LOGGING_CONFIG'])
logger = logging.getLogger(app.config['APP_NAME'])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5000:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config['HOST'], app.config['PORT'])

# Initialize the database session
car_manager = CarManager(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main view that request a dream car from user.

    Create drop down list into index page that uses data queried from
    Car database and inserts it into the app/templates/index.html template.

    Returns:
        Rendered html template

    """
    logger.debug('request method: %s', request.method)

    try:
        # create the form to capture user inputs
        form_user_input = Form()

        # get a list of all makers in the data base
        maker_list = [(makers[0], makers[0]) for makers in (car_manager.session
                                                            .query(Cars.maker)
                                                            .distinct()
                                                            .order_by(Cars.maker)
                                                            .all())]
        logger.debug('Retrieved maker list: %s', maker_list)

        # set makers as choices in the dropdown list
        form_user_input.maker.choices = [('', 'Enter Maker')] + maker_list

        # render index page with the selection form
        logger.info('Rendering index page...')
        return render_template('index.html', form_user_input=form_user_input)

    except sqlite3.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


@app.route('/recommend', methods=['POST'])
def get_recommendations() -> str:
    """Make recommendation using the information submitted by the user.
    Take the form posted by the index page. Validate input and get recommendations
    from database.

    Returns:
        str: The rendered index page.
    """
    logger.info('Getting recommendations for user...')
    logger.debug('Form received: \n%s', request.form)

    try:
        # retrieve variables from user submission
        maker = request.form['maker']
        model = request.form['model']
        year_str = request.form['year']
        bodytype = request.form['bodytype']
        logger.info(
            'User input received.'
            ' \nMaker: %s \nModel: %s \nYear %s \nBodyType: %s',
            maker, model, year_str, bodytype
        )

        # validate if inputs are valid
        validate_input(maker, model, year_str, bodytype)

        # convert year to int if valid
        year = int(year_str)

        # get recommendations
        input_specs = {'maker': maker, 'model': model,
                       'year': year, 'bodytype': bodytype}
        car_recommendations, dream_car = get_recommendation(
            car_manager=car_manager,
            max_rows=app.config['MAX_ROWS_SHOW'],
            **input_specs
        )
        logger.info('Recommendations list retrieved. %s', car_recommendations)
        logger.info('Dream car retrieved. %s', dream_car)

        # render result page
        return render_template(
            'result.html',
            cars=car_recommendations,
            dream_car=dream_car
        )
    except (BadRequestKeyError, ValueError) as missing_input:
        logger.error('Some values are missing from the form.'
                     'Must input all four required attributes:'
                     ' maker, model, year, and body type. '
                     'Message: %s', missing_input)
        return render_template('error_form.html', error_message=missing_input)
    except sqlite3.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


@app.route('/models/<maker>')
def get_models(maker: str) -> Union[Response, str]:
    """Given user's selected maker, query all car models made by that maker,
    and return the model list as a json response.

    Args:
        maker (str): The maker selected by the user.

    Returns:
        Response: flask.Response
    """
    try:
        # retrieve all models built by the maker
        logger.debug('Getting all models for maker %s', maker)
        models = [
            (model[0], model[0]) for model in (
                car_manager.session
                .query(Cars.genmodel)
                .filter(Cars.maker == maker)
                .distinct()
                .order_by(Cars.genmodel)
                .all()
            )
        ]
        logger.info('Get model list: %s', models)

        # create model objects and save in a lists
        model_array = []
        for model in models:
            model_obj = {}
            model_obj['id'] = model[0]
            model_obj['name'] = model[1]
            model_array.append(model_obj)

        # return json object with the model lists
        return jsonify({'models': model_array})
    except sqlite3.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


@app.route('/years/<maker>/<model>')
def get_years(maker: str, model: str) -> Union[Response, str]:
    """Given user's selected maker and car model, query all years in which the car
    was made, and return the year list as a json response.

    Args:
        maker (str): The maker selected by the user.
        model (str): The car model selected by the user.

    Returns:
        Response: flask.Response
    """
    try:
        # retrieve all years of this model
        logger.debug('Getting all years for maker %s model %s',
                     maker, model)
        years = [
            (year[0], year[0]) for year in (
                car_manager.session
                .query(Cars.year)
                .filter(Cars.maker == maker,
                        Cars.genmodel == model)
                .distinct()
                .order_by(Cars.year)
                .all()
            )
        ]
        logger.info('Get year list: %s', years)

        # create model objects and save in a lists
        year_array = []
        for year in years:
            year_obj = {}
            year_obj['id'] = year[0]
            year_obj['name'] = year[1]
            year_array.append(year_obj)

        # return json object with the model lists
        return jsonify({'years': year_array})

    except sqlite3.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


@app.route('/bodytypes/<maker>/<model>/<year>')
def get_body_types(maker: str, model: str, year: str) -> Union[Response, str]:
    """Given user's selected maker, car model and years,
    query all bodytype in which the car, and return the
    bodytype list as a json response.

    Args:
        maker (str): The maker user selected.
        model (str): The mode user selected.
        year (str): The year user selected.

    Returns:
        flask.Response: Jsonify response.
    """

    # retrieve all body types of this model
    logger.debug('Getting all body types for %s %s %s',
                 maker, model, year)

    try:
        # get all possible body types
        bodytypes = [
            (bodytype[0], bodytype[0]) for bodytype in (
                car_manager.session
                .query(Cars.bodytype)
                .filter(Cars.maker == maker,
                        Cars.genmodel == model,
                        Cars.year == year)
                .distinct()
                .order_by(Cars.bodytype)
                .all()
            )
        ]
        logger.info('Get body type list: %s', bodytypes)

        # create model objects and save in a lists
        bodytype_array = []
        for bodytype in bodytypes:
            bodytype_obj = {}
            bodytype_obj['id'] = bodytype[0]
            bodytype_obj['name'] = bodytype[1]
            bodytype_array.append(bodytype_obj)

        # return json object with the model lists
        return jsonify({'bodytypes': bodytype_array})

    except sqlite3.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        port=app.config['PORT'],
        host=app.config['HOST']
    )
