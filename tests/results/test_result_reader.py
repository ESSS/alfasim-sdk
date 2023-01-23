import json

import numpy
import pytest
from barril.curve.curve import Curve
from barril.units import Scalar

from alfasim_sdk.result_reader.reader import GlobalTrendMetadata
from alfasim_sdk.result_reader.reader import OverallTrendMetadata
from alfasim_sdk.result_reader.reader import PositionalTrendMetadata
from alfasim_sdk.result_reader.reader import ProfileMetadata
from alfasim_sdk.result_reader.reader import Results


def test_fail_to_get_curves(results: Results) -> None:
    with pytest.raises(RuntimeError, match="Can not locate"):
        results.get_positional_trend_curve(
            "<invalid property>", "<element name>", (0, "m")
        )

    with pytest.raises(RuntimeError, match="Can not locate"):
        results.get_overall_trend_curve("<invalid property>", "<element name>")

    with pytest.raises(RuntimeError, match="Can not locate"):
        results.get_global_trend_curve("<invalid property>")

    with pytest.raises(RuntimeError, match="Can not locate"):
        results.get_profile_curve("<invalid property>", "<element name>", 0)

    with pytest.raises(IndexError, match="Can not locate"):
        results.get_profile_curve("pressure", "Conexão 1", 999)


def test_profiles(results: Results) -> None:
    assert results.list_profiles() == [
        ProfileMetadata("pressure", "Conexão 1", 14),
        ProfileMetadata("total mass flow rate", "Conexão 1", 14),
    ]
    pressure_initial_1 = results.get_profile_curve("pressure", "Conexão 1", 0)
    pressure_initial_2 = results.get_profile_curve("pressure", "Conexão 1", -14)
    pressure_final_1 = results.get_profile_curve("pressure", "Conexão 1", -1)
    pressure_final_2 = results.get_profile_curve("pressure", "Conexão 1", 13)
    assert isinstance(pressure_initial_1, Curve)
    assert isinstance(pressure_initial_2, Curve)
    assert isinstance(pressure_final_1, Curve)
    assert isinstance(pressure_final_2, Curve)
    # Same domain on initial/final.
    assert pressure_initial_1.domain.GetUnit() == "m"
    assert pressure_final_1.domain.GetUnit() == "m"
    assert numpy.array_equal(
        pressure_initial_1.domain.GetValues(),
        pressure_final_1.domain.GetValues(),
    )
    assert numpy.array_equal(
        pressure_final_1.domain.GetValues(),
        pressure_final_2.domain.GetValues(),
    )
    # Different images initial/final.
    assert pressure_initial_1.image.GetUnit() == "Pa"
    assert pressure_final_1.image.GetUnit() == "Pa"
    assert not numpy.array_equal(
        pressure_initial_1.image.GetValues(),
        pressure_final_1.image.GetValues(),
    )
    assert numpy.array_equal(
        pressure_initial_1.domain.GetValues(),
        pressure_initial_2.domain.GetValues(),
    )
    assert numpy.array_equal(
        pressure_final_1.image.GetValues(),
        pressure_final_2.image.GetValues(),
    )


def test_global_trends(results: Results) -> None:
    assert list(map(str, results.list_global_trends())) == ["timestep"]
    timestep = results.get_global_trend_curve("timestep")
    assert isinstance(timestep, Curve)
    assert len(timestep.domain) == 62
    assert timestep.domain.GetUnit() == "s"
    assert timestep.image.GetUnit() == "s"


def test_list_overall_trends(results: Results) -> None:
    assert results.list_overall_trends() == [
        OverallTrendMetadata("pipe total liquid volume", "Conexão 1"),
    ]
    pipe_total_liquid_volume = results.get_overall_trend_curve(
        "pipe total liquid volume",
        "Conexão 1",
    )
    assert isinstance(pipe_total_liquid_volume, Curve)
    assert len(pipe_total_liquid_volume.domain) == 62
    assert pipe_total_liquid_volume.domain.GetUnit() == "s"
    assert pipe_total_liquid_volume.image.GetUnit() == "m3"


def test_list_positional_trends(results: Results) -> None:
    assert results.list_positional_trends() == [
        PositionalTrendMetadata("mixture temperature", "Conexão 1", Scalar(300.0, "m")),
        PositionalTrendMetadata("pressure", "Conexão 1", Scalar(300.0, "m")),
    ]
    mixture_temperature = results.get_positional_trend_curve(
        "mixture temperature",
        "Conexão 1",
        (300.0, "m"),
    )
    assert isinstance(mixture_temperature, Curve)
    assert mixture_temperature.domain.GetUnit() == "s"
    assert mixture_temperature.image.GetUnit() == "K"


def test_logs(results: Results) -> None:
    log = results.log
    assert "Simulation finished" in log.read_text()

    log_calc = results.log_calc
    assert "NEW TIME-STEP" in log_calc.read_text()

    status = json.loads(results.status.read_text())
    assert status["state"] == "FINISHED"
    assert status["progress"] == 1.0


def test_metadata_string():
    profile = ProfileMetadata("property", "element", 7)
    assert str(profile) == "property@element(timesteps=7)"

    trend = PositionalTrendMetadata("property", "element", Scalar(13, "m"))
    assert str(trend) == "property@element(13 [m])"

    overall_trend = OverallTrendMetadata("property", "element")
    assert str(overall_trend) == "property@element"

    global_trend = GlobalTrendMetadata("property")
    assert str(global_trend) == "property"
