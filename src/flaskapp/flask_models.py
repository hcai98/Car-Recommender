import logging

import pandas as pd
from flask_wtf import FlaskForm 
from wtforms import SelectField

from src.utils import io

logger = logging.getLogger(__name__)

class Form(FlaskForm):
    """A form to get input from users. Users can specify the manufacturer 
    (maker), model, year, and bodytype of their dream car.
    """
    maker = SelectField('Maker', choices=[])
    model = SelectField('Model', choices=[('', 'Enter Model')])
    year = SelectField('Year', choices=[('', 'Enter Year')])
    bodytype = SelectField('Body Type', choices=[('', 'Enter Body Type')])