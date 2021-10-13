from functools import lru_cache


@lru_cache()
def register_units() -> None:
    """
    Register new categories for Barril and limit the number of units shown to users.

    Note: we try to add all combinations of units we find useful, but given that POSC doesn't have all
    possible combinations we remove the ones which don't work manually.
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

    length_units = ["m", "ft", "km", "mm", "in"]
    db.AddCategory(
        "length", quantity_type="length", valid_units=length_units, override=True
    )

    pressure_units = ["bar", "Pa", "kPa", "MPa", "psi", "kgf/cm2", "atm"]
    db.AddCategory(
        "pressure", quantity_type="pressure", valid_units=pressure_units, override=True
    )

    db.AddCategory(
        "temperature",
        quantity_type="temperature",
        valid_units=["degC", "K", "degF"],
        override=True,
    )
    db.AddCategory(
        "dimensionless",
        quantity_type="dimensionless",
        valid_units=["-", "%"],
        override=True,
    )

    mass_units = ["kg", "g", "lbm"]
    db.AddCategory("mass", quantity_type="mass", valid_units=mass_units, override=True)

    time_units = ["d", "s", "h", "min"]
    db.AddCategory("time", quantity_type="time", valid_units=time_units, override=True)

    flow_rate_units = [
        f"{mass_unit}/{time_unit}"
        for mass_unit in mass_units
        for time_unit in time_units
    ]
    flow_rate_units.remove("g/d")
    db.AddCategory(
        "mass flow rate",
        quantity_type="mass flow rate",
        valid_units=flow_rate_units,
        override=True,
    )

    volume_units = ["m3", "cm3", "L", "galUS", "galUK", "ft3", "Mcf"]
    db.AddCategory(
        "volume", quantity_type="volume", valid_units=volume_units, override=True
    )

    density_units = [
        f"{mass_unit}/{volume_unit}"
        for mass_unit in mass_units
        for volume_unit in volume_units
    ]
    density_units.remove("kg/cm3")
    density_units.remove("kg/galUS")
    density_units.remove("kg/galUK")
    density_units.remove("kg/ft3")
    density_units.remove("kg/Mcf")
    density_units.remove("g/ft3")
    density_units.remove("g/Mcf")
    density_units.remove("lbm/m3")
    density_units.remove("lbm/cm3")
    density_units.remove("lbm/L")
    density_units.remove("lbm/Mcf")
    db.AddCategory(
        "density", quantity_type="density", valid_units=density_units, override=True
    )

    velocity_units = [
        f"{length_unit}/{time_unit}"
        for length_unit in length_units
        for time_unit in time_units
    ]
    velocity_units.remove("km/d")
    velocity_units.remove("km/min")
    velocity_units.remove("mm/d")
    velocity_units.remove("mm/h")
    velocity_units.remove("mm/min")
    velocity_units.remove("in/d")
    velocity_units.remove("in/h")
    db.AddCategory(
        "velocity", quantity_type="velocity", valid_units=velocity_units, override=True
    )

    # we don't construct volume_per_volume_units using 'volume_units' because the number of units available by
    # the dimensionless quantity type is really small
    volume_per_volume_units = ["m3/m3", "L/m3", "ft3/ft3", "volppm"]
    db.AddCategory(
        "volume per volume",
        quantity_type="dimensionless",
        valid_units=volume_per_volume_units,
        override=True,
    )

    # Removing two duplicated units from our base
    productivity_index_units = db.GetValidUnits("productivity index")
    if all(unit in productivity_index_units for unit in ["bbl/psi.d", "bbl/d.psi"]):
        productivity_index_units.remove("bbl/d.psi")
    if all(unit in productivity_index_units for unit in ["m3/d.kPa", "m3/kPa.d"]):
        productivity_index_units.remove("m3/d.kPa")
    db.AddCategory(
        "productivity index",
        quantity_type="productivity index",
        valid_units=productivity_index_units,
        override=True,
    )

    # Creating separate categories for some Gas properties, so they are plotted in a separate axis
    std_volume_per_time_units = db.GetValidUnits("standard volume per time")
    db.AddCategory(
        "gas standard volume per time",
        quantity_type="standard volume per time",
        valid_units=std_volume_per_time_units,
    )

    std_volume_units = db.GetValidUnits("standard volume")
    db.AddCategory(
        "gas standard volume",
        quantity_type="standard volume",
        valid_units=std_volume_units,
    )
    # NOTE: "gas volume flow rate" and "gas volume" are also required, but they are already registered

    # TODO: ASIM-4452: Add "force per square velocity" to barril and update PIG quadratic friction
    # After the issue above is solved, the code below may be removed
    from barril.units.posc import MakeCustomaryToBase
    from barril.units.posc import MakeBaseToCustomary

    old_unit = "Ns/m"
    quantity_type = db.GetQuantityType(old_unit)
    unit_name = db.GetUnitName(quantity_type, old_unit)

    f_unit_to_base = MakeCustomaryToBase(0.0, 1.0, 1.0, 0.0)
    f_base_to_unit = MakeBaseToCustomary(0.0, 1.0, 1.0, 0.0)
    db.AddUnit(
        quantity_type=quantity_type,
        name=unit_name,
        unit="N.s/m",
        frombase=f_unit_to_base,
        tobase=f_base_to_unit,
        default_category="force per velocity",
    )
    db.AddCategory(
        "force per velocity",
        "force per velocity",
        valid_units=["N.s/m", "lbf.s/ft", "lbf.s/in", "kgf.s/m"],
        override=True,
    )

    db.AddUnitBase(
        "force per velocity squared",
        "Newton second squared per meter squared",
        "N.s2/m2",
    )

    f_unit_to_base = MakeCustomaryToBase(0.0, 47.8802631216, 1.0, 0.0)
    f_base_to_unit = MakeBaseToCustomary(0.0, 47.8802631216, 1.0, 0.0)
    db.AddUnit(
        "force per velocity squared",
        "Pound force second squared per foot squared",
        "lbf.s2/ft2",
        f_base_to_unit,
        f_unit_to_base,
        default_category=None,
    )
    f_unit_to_base = MakeCustomaryToBase(0.0, 6894.75788952, 1.0, 0.0)
    f_base_to_unit = MakeBaseToCustomary(0.0, 6894.75788952, 1.0, 0.0)
    db.AddUnit(
        "force per velocity squared",
        "Pound force second squared per inch squared",
        "lbf.s2/in2",
        f_base_to_unit,
        f_unit_to_base,
        default_category=None,
    )
    f_unit_to_base = MakeCustomaryToBase(0.0, 9.80665, 1.0, 0.0)
    f_base_to_unit = MakeBaseToCustomary(0.0, 9.80665, 1.0, 0.0)
    db.AddUnit(
        "force per velocity squared",
        "Kilogram force second squared per meter squared",
        "kgf.s2/m2",
        f_base_to_unit,
        f_unit_to_base,
        default_category=None,
    )
    db.AddCategory(
        "force per velocity squared",
        "force per velocity squared",
        valid_units=["N.s2/m2", "lbf.s2/ft2", "lbf.s2/in2", "kgf.s2/m2"],
        override=True,
    )
