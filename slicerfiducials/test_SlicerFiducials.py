# -*- coding: utf-8 -*-
# File: test_SlicerFiducials.py
# Author: Arjit Jain <thearjitjain@gmail.com>
import numpy as np
import pandas as pd

import nose

from .slicerfiducials import SlicerFiducials

original = SlicerFiducials(
    name="../BCD_Original.fcsv",
    image="../sub-XXXXX_ses-YYYYY_run-002_echo-1_T1w.nii.gz",
)
original_markup = SlicerFiducials(name="../BCD_Original_markup.fcsv")


def test_euclidean_with_correct_fids():
    nose.tools.assert_almost_equal(original.euclidean_distance("RE", "LE"), 64.53, 1)
    nose.tools.assert_almost_equal(original.euclidean_distance("LE", "RE"), 64.53, 1)
    nose.tools.assert_almost_equal(
        original_markup.euclidean_distance("RE", "LE"), 64.53, 1
    )
    nose.tools.assert_almost_equal(
        original_markup.euclidean_distance("LE", "RE"), 64.53, 1
    )
    nose.tools.assert_almost_equal(original_markup.euclidean_distance("LE", "LE"), 0, 5)
    nose.tools.assert_almost_equal(original.euclidean_distance("RE", "RE"), 0, 5)


def test_euclidean_with_wrong_inputs():
    try:
        original.euclidean_distance("Left Hand", "Right Hand")
    except KeyError:
        assert True
    except:
        assert False


def test_names():
    names = [
        "AC",
        "BPons",
        "CM",
        "LE",
        "PC",
        "RE",
        "RP",
        "RP_front",
        "SMV",
        "VN4",
        "callosum_left",
        "callosum_right",
        "dens_axis",
        "genu",
        "l_caud_head",
        "l_corp",
        "l_front_pole",
        "l_inner_corpus",
        "l_lat_ext",
        "l_occ_pole",
        "l_prim_ext",
        "l_sup_ext",
        "l_temp_pole",
        "lat_left",
        "lat_right",
        "lat_ven_left",
        "lat_ven_right",
        "left_cereb",
        "left_lateral_inner_ear",
        "m_ax_inf",
        "m_ax_sup",
        "mid_basel",
        "mid_lat",
        "mid_prim_inf",
        "mid_prim_sup",
        "mid_sup",
        "optic_chiasm",
        "r_caud_head",
        "r_corp",
        "r_front_pole",
        "r_inner_corpus",
        "r_lat_ext",
        "r_occ_pole",
        "r_prim_ext",
        "r_sup_ext",
        "r_temp_pole",
        "right_lateral_inner_ear",
        "rostrum",
        "rostrum_front",
        "top_left",
        "top_right",
    ]
    assert original.names() == names
    assert original_markup.names() == names


def test_query():
    assert np.allclose(
        original.query("LE"),
        np.array([30.672317504882816, -64.453857421875, 13.664093017578123]),
    )
    assert np.allclose(original_markup.query("LE"), np.array([30.672, -64.454, 13.664]))
    assert np.allclose(
        original.query("LE", space="index"),
        np.array([203.0, 170.00057892364634, 312.0]),
    )
    try:
        original_markup.query("LE", space="index")
    except AssertionError:
        assert True
    except:
        assert False


def test_diff():
    diff = SlicerFiducials.diff_files(original_markup, original)
    for i in diff.names():
        assert np.allclose(diff.query(i), np.array([0, 0, 0]), atol=1, rtol=0)


def test_get_format():
    pd.testing.assert_frame_equal(
        original_markup.df,
        original_markup.get_format("original_markup"),
        check_dtype=False,
        check_less_precise=1,
    )
    pd.testing.assert_frame_equal(
        original.df,
        original.get_format("original"),
        check_dtype=False,
        check_less_precise=1,
    )
    pd.testing.assert_frame_equal(
        original_markup.df,
        original.get_format("original_markup"),
        check_dtype=False,
        check_less_precise=1,
    )
    pd.testing.assert_frame_equal(
        original.df,
        original_markup.get_format("original"),
        check_dtype=False,
        check_less_precise=1,
    )


if __name__ == "__main__":
    nose.run()
