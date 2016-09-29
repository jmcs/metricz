#!/usr/bin/env python
# -*- coding: utf-8 -*-

from metricz import MetricWriter
from metricz.metricz import KAIROSDB_URL

import datetime
from mock import MagicMock, ANY
import pytest


@pytest.fixture(autouse=True)
def mock_token(monkeypatch):
    mocked_tokens_gen = MagicMock(name='Token Gen')
    mocked_tokens_gen.get = MagicMock(return_value='ABCabc')
    monkeypatch.setattr('metricz.metricz.tokens', mocked_tokens_gen)
    return mocked_tokens_gen


@pytest.fixture(autouse=True)
def freeze_datetime(monkeypatch):
    current_time = datetime.datetime(2016, 9, 29, 0, 0)
    mocked_datetime = MagicMock()
    mocked_datetime.utcnow = MagicMock(return_value=current_time)
    monkeypatch.setattr('metricz.metricz.datetime', mocked_datetime)
    return mocked_datetime


@pytest.fixture
def requests_mock(monkeypatch):
    mocked_requests = MagicMock(name='mocked requests')
    mocked_requests.session = MagicMock(return_value=mocked_requests)
    monkeypatch.setattr('metricz.metricz.requests', mocked_requests)
    return mocked_requests


def test_write_with_timeout(requests_mock):
    # use the default one
    metric_writer = MetricWriter()
    metric_writer.write_metric('foobar', 1, {"foo": "bar"})
    requests_mock.post.assert_called_with(
        KAIROSDB_URL,
        data=ANY,
        timeout=4)

    # use the timeout in the call
    metric_writer = MetricWriter()
    metric_writer.write_metric('foobar', 1, {"foo": "bar"}, timeout=10)
    requests_mock.post.assert_called_with(
        KAIROSDB_URL,
        data=ANY,
        timeout=10)

    # use the timeout in the MetricWriter class
    metric_writer = MetricWriter(timeout=5)
    metric_writer.write_metric('foobar', 1, {"foo": "bar"})
    requests_mock.post.assert_called_with(
        KAIROSDB_URL,
        data=ANY,
        timeout=5)
