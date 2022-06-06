import json
import logging.config
import sqlite3
import traceback

import sqlalchemy.exc
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask import session as flask_session
from werkzeug.exceptions import BadRequestKeyError

# For setting up the Flask-SQLAlchemy database session
from src.database.create_db import Cars
from src.database.add_cars import CarManager
from src.flaskapp.flask_models import Form
from src.flaskapp.recommend import validate_input, get_recommendation

# Initialize the Flask application
app = Flask(__name__,
            template_folder="app/templates",
            static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5000:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config["HOST"], app.config["PORT"])

# Initialize the database session
car_manager = CarManager(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the app/templates/index.html template.

    Returns:
        Rendered html template

    """
    logger.info('request method: %s', request.method)

    try:
        # create the form to capture user inputs
        form_user_input = Form()

        # get a list of all makers in the data base
        maker_list = [(makers[0], makers[0]) for makers in (car_manager.session
                                                            .query(Cars.maker).distinct().all())]
        logger.debug('Retrieved maker list: %s', maker_list)

        # set maker choices in form
        form_user_input.maker.choices = [('', 'Enter Maker')] + maker_list

        # if request.method == 'POST':
        #     cars = car_manager.session.query(Cars).filter(Cars.cluster == 42).limit(
        #         app.config["MAX_ROWS_SHOW"]
        #     ).all()
        #     logger.debug("Index page accessed")
        #     return '<h1>Hello</h1>'
        logger.info("Rendering without cars.")

        try:
            return render_template('index.html',
                                   form_user_input=form_user_input,
                                   cars=request.args['cars'])
        except:
            return render_template('index.html',
                                   form_user_input=form_user_input)

    except sqlite3.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except:
        traceback.print_exc()
        logger.error("Not able to display cars, error page returned")
        return render_template('error.html')


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    logger.info('Getting recommendations for user...')

    logger.debug('Form received: \n%s', request.form)
    try:
        # retrieve variables from user submission
        maker = request.form['maker']
        model = request.form['model']
        year = request.form['year']
        bodytype = request.form['bodytype']
        logger.info("User input received."
                    " \nMaker: %s \nModel: %s \nYear %s \nBodyType: %s",
                    maker, model, year, bodytype)

        # validate if inputs are valid
        validate_input(maker, model, year, bodytype)
        year = int(year)  # convert year to int if valid

        input_specs = {'maker': maker, 'model': model,
                       'year': year, 'bodytype': bodytype}

        # get recommendations
        car_recommendations, dream_car = get_recommendation(car_manager=car_manager,
                                                            max_rows=app.config["MAX_ROWS_SHOW"],
                                                            **input_specs)
        logger.info('Recommendations list retrieved. %s', car_recommendations)
        logger.info('Dream car retrieved. %s', dream_car)

        return render_template('result.html', cars=car_recommendations, dream_car=dream_car)

    except (BadRequestKeyError, ValueError) as missing_input:
        logger.error("Some values are missing from the form."
                     "Must input all four required attributes:"
                     " maker, model, year, and body type. "
                     "Message: %s", missing_input)
        return render_template('error_form.html', error_message=missing_input)
    except sqlite3.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')

@app.route('/models/<maker>')
def get_models(maker: str):

    try:
        # retrieve all models built by the maker
        logger.debug("Getting all models for maker %s", maker)
        models = [(model[0], model[0]) for model in (car_manager.session
                                                    .query(Cars.genmodel)
                                                    .filter(Cars.maker == maker)
                                                    .distinct()
                                                    .all())]
        logger.info('Get model list: %s', models)

        # create model objects and save in a lists
        model_array = []
        for model in models:
            modelObj = {}
            modelObj['id'] = model[0]
            modelObj['name'] = model[1]
            model_array.append(modelObj)

        # return json object with the model lists
        return jsonify({'models': model_array})

    except sqlite3.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')

@app.route('/years/<maker>/<model>')
def get_years(maker: str, model: str):

    try:
        # retrieve all years of this model
        logger.debug("Getting all years for maker %s model %s",
                    maker, model)
        years = [(year[0], year[0]) for year in (car_manager.session
                                                .query(Cars.year)
                                                .filter(Cars.maker == maker,
                                                        Cars.genmodel == model)
                                                .distinct()
                                                .all())]
        logger.info('Get year list: %s', years)

        # create model objects and save in a lists
        year_array = []
        for year in years:
            yearObj = {}
            yearObj['id'] = year[0]
            yearObj['name'] = year[1]
            year_array.append(yearObj)

        # return json object with the model lists
        return jsonify({'years': year_array})

    except sqlite3.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')


@app.route('/bodytypes/<maker>/<model>/<year>')
def get_body_types(maker: str, model: str, year: str):

    # retrieve all body types of this model
    logger.debug("Getting all body types for %s %s %s",
                 maker, model, year)
    
    try:
        bodytypes = [(bodytype[0], bodytype[0]) for bodytype in (car_manager.session
                                                                .query(Cars.bodytype)
                                                                .filter(Cars.maker == maker,
                                                                        Cars.genmodel == model,
                                                                        Cars.year == year)
                                                                .distinct()
                                                                .all())]
        logger.info('Get body type list: %s', bodytypes)

        # create model objects and save in a lists
        bodytype_array = []
        for bodytype in bodytypes:
            bodytypeObj = {}
            bodytypeObj['id'] = bodytype[0]
            bodytypeObj['name'] = bodytype[1]
            bodytype_array.append(bodytypeObj)

        # return json object with the model lists
        return jsonify({'bodytypes': bodytype_array})

    except sqlite3.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as err_or:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], err_or)
        return render_template('error.html')

if __name__ == '__main__':
    app.run(
        debug=app.config["DEBUG"],
        port=app.config["PORT"],
        host=app.config["HOST"]
    )
