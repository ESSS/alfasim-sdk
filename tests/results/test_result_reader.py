from __future__ import annotations

from pathlib import Path

import attr
import numpy
import numpy as np
import pytest
from barril.curve.curve import Curve
from barril.units import Array, Scalar

from alfasim_sdk.result_reader.aggregator import (
    GlobalSensitivityAnalysisMetadata,
    GSAOutputKey,
    HistoricDataCurveMetadata,
    HistoryMatchingMetadata,
    HMOutputKey,
    UncertaintyPropagationAnalysesMetaData,
    UPOutputKey,
    read_history_matching_metadata,
    read_history_matching_result,
)
from alfasim_sdk.result_reader.reader import (
    GlobalSensitivityAnalysisResults,
    GlobalTrendMetadata,
    HistoryMatchingDeterministicResults,
    HistoryMatchingProbabilisticResults,
    OverallTrendMetadata,
    PositionalTrendMetadata,
    ProfileMetadata,
    Results,
    UncertaintyPropagationResults,
)


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


def test_status(results: Results, datadir: Path) -> None:
    # Status exist.
    status = results.status
    assert status["state"] == "FINISHED"
    assert status["progress"] == 1.0

    # Status do not exist, should be None.
    non_existent_results = Results(datadir / "foo.data")
    assert non_existent_results.status is None


def test_metadata_string():
    profile = ProfileMetadata("property", "element", 7)
    assert str(profile) == "property@element(timesteps=7)"

    trend = PositionalTrendMetadata("property", "element", Scalar(13, "m"))
    assert str(trend) == "property@element(13 [m])"

    overall_trend = OverallTrendMetadata("property", "element")
    assert str(overall_trend) == "property@element"

    global_trend = GlobalTrendMetadata("property")
    assert str(global_trend) == "property"


def test_global_sensitivity_analysis_results_reader(
    global_sa_results_dir: Path,
) -> None:
    results = GlobalSensitivityAnalysisResults.from_directory(global_sa_results_dir)

    assert results.get_sensitivity_curve(
        "temperature", "trend_id_1", "parametric_var_1"
    ) == Curve(
        image=Array("dimensionless", [11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7], "-"),
        domain=Array("time", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], "s"),
    )
    assert results.get_sensitivity_curve(
        "temperature", "trend_id_1", "parametric_var_2"
    ) == Curve(
        image=Array("dimensionless", [12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7], "-"),
        domain=Array("time", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], "s"),
    )

    assert results.metadata.items[
        GSAOutputKey("temperature", "parametric_var_1", "trend_id_1")
    ] == GlobalSensitivityAnalysisMetadata.GSAItem(
        property_id="temperature",
        trend_id="trend_id_1",
        category="dimensionless",
        network_element_name="Conexao 1",
        position=100.0,
        position_unit="m",
        unit="-",
        parametric_var_id="parametric_var_id_1",
        parametric_var_name="A",
        qoi_index=0,
        qoi_data_index=0,
    )

    # Test equality check.
    assert results == attr.evolve(results)
    assert results != object()
    assert results != attr.evolve(results, timeset=np.array([0.1, 0.2]))

    # Ensure the reader can handle a nonexistent result file.
    results = GlobalSensitivityAnalysisResults.from_directory(Path("foo"))
    assert results is None


class TestHistoryMatchingResultsReader:
    def test_deterministic_reader(self, hm_deterministic_results_dir: Path) -> None:
        results = HistoryMatchingDeterministicResults.from_directory(
            hm_deterministic_results_dir
        )
        assert results.deterministic_values == {
            HMOutputKey("parametric_var_1"): 0.1,
            HMOutputKey("parametric_var_2"): 3.2,
        }
        self._validate_meta_and_historic_curves(results)

        # Test equality check.
        assert results == attr.evolve(results)
        assert results != object()
        assert results != attr.evolve(
            results, deterministic_values={HMOutputKey("parametric_var_1"): 0.1}
        )

    def test_probabilistic_reader(self, hm_probabilistic_results_dir: Path) -> None:
        results = HistoryMatchingProbabilisticResults.from_directory(
            hm_probabilistic_results_dir
        )
        np.testing.assert_equal(
            results.probabilistic_distributions,
            {
                HMOutputKey("parametric_var_1"): np.array([0.1, 0.22, 1.0, 0.8, 0.55]),
                HMOutputKey("parametric_var_2"): np.array([3.0, 6.0, 5.1, 4.7, 6.3]),
            },
        )
        self._validate_meta_and_historic_curves(results)

        # Test equality check.
        assert results == attr.evolve(results)
        assert results != object()
        assert results != attr.evolve(
            results,
            probabilistic_distributions={
                HMOutputKey("parametric_var_1"): np.array([0.1, 0.3])
            },
        )

    def test_wrong_result_file(
        self, hm_probabilistic_results_dir: Path, hm_deterministic_results_dir: Path
    ) -> None:
        """
        Check that the field validator correctly prevent one from using the deterministic
        reader to read probabilistic results and vice-versa.
        """
        prob_metadata = read_history_matching_metadata(hm_probabilistic_results_dir)
        prob_values = read_history_matching_result(
            hm_probabilistic_results_dir, prob_metadata, "HM-probabilistic"
        )

        with pytest.raises(
            ValueError,
            match=r".*deterministic_values.*should be.*float.*received.*ndarray.*",
        ):
            HistoryMatchingDeterministicResults(
                historic_data_curves={},
                metadata=prob_metadata,
                deterministic_values=prob_values,
            )

        det_metadata = read_history_matching_metadata(hm_deterministic_results_dir)
        det_values = read_history_matching_result(
            hm_deterministic_results_dir, det_metadata, "HM-deterministic"
        )

        with pytest.raises(
            ValueError,
            match=r".*probabilistic_distributions.*should be.*ndarray.*received.*float.*",
        ):
            HistoryMatchingProbabilisticResults(
                historic_data_curves={},
                metadata=det_metadata,
                probabilistic_distributions=det_values,
            )

    def _validate_meta_and_historic_curves(
        self,
        results: (
            HistoryMatchingDeterministicResults | HistoryMatchingProbabilisticResults
        ),
    ) -> None:
        assert results.historic_data_curves == {
            "observed_curve_1": (
                HistoricDataCurveMetadata(
                    curve_id="observed_curve_1",
                    curve_name="curve 1",
                    domain_unit="s",
                    image_unit="m3/m3",
                    image_category="volume fraction",
                ),
                Curve(
                    image=Array("volume fraction", np.array([0.1, 0.5, 0.9]), "m3/m3"),
                    domain=Array("time", np.array([1.1, 2.2, 3.3]), "s"),
                ),
            ),
            "observed_curve_2": (
                HistoricDataCurveMetadata(
                    curve_id="observed_curve_2",
                    curve_name="curve 2",
                    domain_unit="s",
                    image_unit="Pa",
                    image_category="pressure",
                ),
                Curve(
                    image=Array("pressure", np.array([1.0, 5.0, 9.0, 3.1]), "Pa"),
                    domain=Array("time", np.array([1.2, 2.3, 3.4, 4.5]), "s"),
                ),
            ),
        }
        assert results.metadata.hm_items == {
            HMOutputKey("parametric_var_1"): HistoryMatchingMetadata.HMItem(
                parametric_var_id="parametric_var_1",
                parametric_var_name="mg",
                min_value=0.0,
                max_value=1.0,
                data_index=0,
            ),
            HMOutputKey("parametric_var_2"): HistoryMatchingMetadata.HMItem(
                parametric_var_id="parametric_var_2",
                parametric_var_name="mo",
                min_value=2.5,
                max_value=7.5,
                data_index=1,
            ),
        }


def test_uncertainty_propagation_results_reader(up_results_dir: Path) -> None:
    reader = UncertaintyPropagationResults.from_directory(up_results_dir)

    assert np.allclose(
        reader.timeset, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    )
    assert len(reader.results) == 2
    some_result = reader.results[
        UPOutputKey(property_name="absolute_pressure", element_name="trend_id_1")
    ]
    assert np.allclose(
        some_result.mean_result, np.array([12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7])
    )
    assert len(reader.metadata.items) == 2
    assert reader.metadata.items[
        UPOutputKey(property_name="temperature", element_name="trend_id_1")
    ] == UncertaintyPropagationAnalysesMetaData.UPItem(
        property_id="temperature",
        trend_id="trend_id_1",
        category="temperature",
        network_element_name="Conexao 1",
        position=100.0,
        position_unit="m",
        unit="K",
        samples=5,
        result_index=0,
        sample_indexes=[[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
    )

    # Test equality check.
    assert reader == attr.evolve(reader)
    assert reader != object()
    assert reader != attr.evolve(reader, timeset=np.array([0.1, 0.2]))

    # Ensure the reader can handle a nonexistent result file.
    reader = UncertaintyPropagationResults.from_directory(Path("foo"))
    assert reader is None
