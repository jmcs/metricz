#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from metricz.cli import main

FAKE_ENV = {
    'OAUTH2_ACCESS_TOKEN_URL': 'oauth.example.com',
    'CREDENTIALS_DIR': '/meta/credentials',
    'METRICZ_DB_URL': 'kairosdb.example.com'
}


@pytest.fixture(autouse=True)
def metric_writer(monkeypatch):
    metric_writer_instance = MagicMock(name="MetricWriter()")
    monkeypatch.setattr('metricz.cli.MetricWriter', MagicMock(return_value=metric_writer_instance))
    return metric_writer_instance


@pytest.fixture(autouse=True)
def default_tags():
    return {'hostname': socket.gethostname()}


@pytest.fixture()
def runner():
    return CliRunner(env=FAKE_ENV)


def test_write_metric(runner, metric_writer, default_tags):
    result = runner.invoke(main, ['write', 'something', '1'],
                           catch_exceptions=False)
    assert result.exit_code == 0
    metric_writer.write_metric.assert_called_once_with('something', 1, default_tags)

    metric_writer.reset_mock()
    result = runner.invoke(main, ['write', 'other.thing', '24'],
                           catch_exceptions=False)
    assert result.exit_code == 0
    metric_writer.write_metric.assert_called_once_with('other.thing', 24, default_tags)


def test_write_metric_with_tags(runner, metric_writer, default_tags):
    result = runner.invoke(main, ['write', 'answer', '42', 'question=all.the.things'],
                           catch_exceptions=False)
    assert result.exit_code == 0
    expected_tags = {'question': 'all.the.things'}
    expected_tags.update(default_tags)
    metric_writer.write_metric.assert_called_once_with(
        'answer', 42, expected_tags)

    metric_writer.reset_mock()
    result = runner.invoke(main, ['write', 'other.thing', '1', 'some=tag', 'other=thing'],
                           catch_exceptions=False)
    assert result.exit_code == 0
    expected_tags = {'some': 'tag', 'other': 'thing'}
    expected_tags.update(default_tags)
    metric_writer.write_metric.assert_called_once_with(
        'other.thing', 1, expected_tags)

    metric_writer.reset_mock()
    result = runner.invoke(main, ['write', 'more', '7', 'some=crazy=tag'],
                           catch_exceptions=False)
    assert result.exit_code == 0
    expected_tags = {'some': 'crazy=tag'}
    expected_tags.update(default_tags)
    metric_writer.write_metric.assert_called_once_with(
        'more', 7, expected_tags)


def test_wrong_write_metric(runner):
    result = runner.invoke(main, ['write'], catch_exceptions=False)
    assert result.exit_code >= 1

    result = runner.invoke(main, ['write', 'something'],
                           catch_exceptions=False)
    assert result.exit_code >= 1


def test_invalid_tags_usage(runner):
    result = runner.invoke(main, ['write', 'other.thing', '1', 'sometag', 'other=thing'],
                           catch_exceptions=False)
    assert 'Invalid tag sometag. Tags should be in the form of key=value' in result.output
    assert result.exit_code == 2


def test_missing_configs_uses_defaults():
    env_missing_envs = {}
    return CliRunner()
    result = runner.invoke(main, ['write', 'thing', '1'],
                           env=env_missing_envs, catch_exceptions=False)
    assert result.exit_code == 0
