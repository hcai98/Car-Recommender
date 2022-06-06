import logging

from src.database.create_db import Cars
from src.database.add_cars import CarManager

logger = logging.getLogger(__name__)


def validate_input(maker: str,
                   model: str,
                   year: str,
                   bodytype: str) -> None:
    """Validate if user input is empty.

    Args:
        maker (str): Manufacturer of the car.
        model (str): Specific of the car.
        year (str): Year when the car was produced.
        bodytype (str): Body type of the car.

    Raises:
        ValueError: Some value missing.
    """
    logger.debug("Validating: %s, %s, %s, %s", maker, model, year, bodytype)

    if maker == '':
        raise ValueError('Maker missing.')
    elif model == '':
        raise ValueError('Model missing.')
    elif year == '':
        raise ValueError('Year missing.')
    elif bodytype == '':
        raise ValueError('Body type missing.')


def get_recommendation(car_manager: CarManager,
                       maker: str,
                       model: str,
                       year: int,
                       bodytype: str,
                       max_rows: int):
    """Recommend cars from the same cluster as the input.

    Args:
        car_manager (CarManager): Manage connection to the car database.
        maker (str): Manufacturer of the car.
        model (str): Specific model of the car.
        year (int): Year of production.
        bodytype (str): Body type of the car.
        max_rows (int): Maximum number of recommendations to be displayed.

    Returns:
        _type_: _description_
    """
    logger.debug("Recommending by: %s, %s, %s, %s", maker, model, year, bodytype)

    # get full specification of the input cars for display
    dream_car = (
        car_manager.session
        .query(Cars)
        .filter(Cars.maker == maker,
                Cars.genmodel == model,
                Cars.year == year,
                Cars.bodytype == bodytype)
        .all()
    )[0]
    
    # retrieve cluster from saved prediction data
    cluster = dream_car.cluster

    # get cars in the same cluster as recommendations
    car_recommend = (
        car_manager.session
        .query(Cars)
        .filter(Cars.cluster == cluster)
        .limit(max_rows)
        .all()
    )

    return car_recommend, dream_car
