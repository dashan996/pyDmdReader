"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""


import os
import pandas as pd
import pytest
from pyDmdReader import DmdReader, TimestampFormat


SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data", "simple.dmd")
SYNCASYNC_DMD = os.path.join(os.path.dirname(__file__), "data", "syncasync.dmd")
INTERNAL_DMD = "DMD_DEMO_FILE"


def test_check_invalid_name():
    dmd = DmdReader(INTERNAL_DMD)
    with pytest.raises(KeyError):
        dmd.read_dataframe("INVALID")
    dmd.close()


def test_check_timestamp_none():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert isinstance(data.index, pd.RangeIndex)
    dmd.close()


def test_check_timestamp_seconds():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert isinstance(data.index, pd.Float64Index)
    dmd.close()


def test_check_timestamp_absolute_local():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert isinstance(data.index, pd.DatetimeIndex)
    assert data.iloc[0].name == pd.Timestamp("2021-08-05T12:21:27.2708+0200", tz="UTC+02:00")
    dmd.close()


def test_check_timestamp_absolute_utc():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert isinstance(data.index, pd.DatetimeIndex)
    assert data.iloc[0].name == pd.Timestamp("2021-08-05T10:21:27.2708", tz="UTC")
    dmd.close()


def test_check_multichannel():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(
        [dmd.channel_names[0], dmd.channel_names[1]], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME
    )
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert column_names == [dmd.channel_names[0], dmd.channel_names[1]]
    dmd.close()


def test_check_multichannel_notimestamp():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0:3], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert column_names == dmd.channel_names[0:3]
    dmd.close()


def test_timerange_start():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=3, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 30001
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 5
    assert data.index[-1] == 8

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=6, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 20001
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 6
    assert data.index[-1] == 8

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 1
    assert data.index[-1] == 8

    dmd.close()


def test_timerange_end():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], end_time=3, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10001
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 1
    assert data.index[-1] == 2

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10002
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 1
    assert data.index[-1] == 5

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert data.empty

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=1.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 5001
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 1
    assert data.index[-1] == 1.5
    
    dmd.close()


def test_timerange_both():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=1.5, end_time=5.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10002
    assert isinstance(data.index, pd.Float64Index)
    assert data.index[0] == 1.5
    assert data.index[-1] == 5.5

    dmd.close()


def test_timerange_simple():
    dmd = DmdReader(SIMPLE_DMD)
    # The file has one sweeps [0 - 0.633] but a recording offset to acquisition start
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0, end_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 5001
    assert data.index[0] == 0
    assert data.index[-1] == 0.5

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0.1, end_time=0.4, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 3001
    assert round(data.index[0], 2) == 0.1
    assert round(data.index[-1], 2) == 0.4

    dmd.close()


def test_async():
    dmd = DmdReader(SYNCASYNC_DMD)
    # The file has one sweeps [0 - 0.633] but a recording offset to acquisition start
    all_data_sync = dmd.read_dataframe(dmd.channel_names[0])
    all_data_async = dmd.read_dataframe(dmd.channel_names[1])
    assert len(all_data_sync) == 29315
    assert len(all_data_async) == 293
    assert all_data_sync.index[0] == 0
    assert round(all_data_sync.index[-1], 3) == round(dmd.measurement_duration, 3)
    assert round(all_data_async.index[0], 2) == 0.01 # Async average with 100 Hz
    assert round(all_data_async.index[-1], 2) == 2.93

    rng_data_sync = dmd.read_dataframe(dmd.channel_names[0], start_time=0.5, end_time=1.5)
    rng_data_async = dmd.read_dataframe(dmd.channel_names[1], start_time=0.5, end_time=1.5)
    assert len(rng_data_sync) == 10001
    assert len(rng_data_async) == 101
    
    assert round(rng_data_sync.index[0], 3) == 0.5
    assert round(rng_data_sync.index[-1], 3) == 1.5
    assert round(rng_data_async.index[0], 2) == 0.5
    assert round(rng_data_async.index[-1], 2) == 1.5

    dmd.close()