


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

    if maker == '':
        raise ValueError('Maker missing.')
    elif model == '':
        raise ValueError('Model missing.')
    elif year == '':
        raise ValueError('Year missing.')
    elif bodytype == '':
        raise ValueError('Body type missing.')
