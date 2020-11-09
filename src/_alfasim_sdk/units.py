from functools import lru_cache


@lru_cache()
def register_units():
    """
    Register new categories for Barril
    """

    from barril.units import UnitDatabase

    db = UnitDatabase.GetSingleton()

    def add_category_if_not_defined(*, category, quantity_type, valid_units):
        if category not in db.categories_to_quantity_types.keys():
            db.AddCategory(
                category=category, quantity_type=quantity_type, valid_units=valid_units
            )

    add_category_if_not_defined(
        category="flow pattern", quantity_type="dimensionless", valid_units=["-"]
    )
    add_category_if_not_defined(
        category="emissivity", quantity_type="dimensionless", valid_units=["-"]
    )
    add_category_if_not_defined(
        category="volume fraction",
        quantity_type="dimensionless",
        valid_units=["-", "%", "m3/m3"],
    )
    add_category_if_not_defined(
        category="mass fraction",
        quantity_type="dimensionless",
        valid_units=["-", "%", "kg/kg", "g/g", "lbm/lbm"],
    )
