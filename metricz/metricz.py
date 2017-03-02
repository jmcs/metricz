# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import json
import pprint
import os

import requests
import tokens

CREDENTIALS_DIR = '/meta/credentials'
OAUTH2_ACCESS_TOKEN_URL = 'https://token.auth.example.com'
TOKEN_RENEWAL_PERIOD = datetime.timedelta(hours=1)

KAIROSDB_URL = 'https://kairosdb.example.com'

EPOCH = datetime.datetime.utcfromtimestamp(0)


def handle_request_errors(response):
    """
    Handles potential errors that were not silenced
    :type response: requests.Response
    """

    try:
        response.raise_for_status()
    except requests.HTTPError:
        try:
            error = pprint.pformat(response.json())
        except json.JSONDecodeError:
            error = response.content
        print("Response: \n", error)
        raise


class MetricWriter(object):
    """
    Interface class to write metrics to the Bus kairosdb.
    """
    def __init__(self,
                 url=os.environ.get('OAUTH2_ACCESS_TOKEN_URL', OAUTH2_ACCESS_TOKEN_URL),
                 directory=os.environ.get('CREDENTIALS_DIR', CREDENTIALS_DIR),
                 kairosdb_url=os.environ.get('KAIROSDB_URL', KAIROSDB_URL),
                 fail_silently=True,
                 timeout=4):
        tokens.configure(url=url, dir=directory)
        tokens.manage('uid', ['uid'])
        tokens.start()
        self.token_ts = None
        self.fail_silently = fail_silently
        self.requests = requests.session()
        self.timeout = timeout
        self._renew_token()
        self.deferred_metrics = []
        self.kairosdb_url = kairosdb_url

    def _renew_token(self):
        """
        Renews the oauth2 token if it's older than the renewal period.

        :return: None
        :rtype: None
        """
        now = datetime.datetime.utcnow()
        if not self.token_ts or (now - TOKEN_RENEWAL_PERIOD) > self.token_ts:
            token = tokens.get('uid')
            self.token_ts = now
            self.requests.headers.update({
                'Authorization': 'Bearer {}'.format(token)
            })

    def write_metric(self, metric_name, value, tags, timestamp=None, timeout=None):
        """
        Writes a metric to kairosdb.

        :param metric_name: The name of the metric.
        :type metric_name: str
        :param value: The value of the metric.
        :type value: int
        :param tags: Tags to add to the metric.
        :type tags: dict
        :param timestamp: The time (IN UTC!) to register the metric. (Default:
                          now)
        :type timestamp: datetime.datetime
        :return: None
        :rtype: None
        """
        payload = self._construct_payload(metric_name, value, tags, timestamp)
        response = self.requests.post(self.kairosdb_url, data=json.dumps(payload), timeout=timeout or self.timeout)

        if not self.fail_silently:
            handle_request_errors(response)

    def defer_metric(self, metric_name, value, tags, timestamp=None):
        """
        Defers a metric write to kairosdb, .

        :param metric_name: The name of the metric.
        :type metric_name: str
        :param value: The value of the metric.
        :type value: int
        :param tags: Tags to add to the metric.
        :type tags: dict
        :param timestamp: The time to register the metric. (Default: now)
        :type timestamp: datetime.datetime
        :return: None
        :rtype: None
        """
        payload = self._construct_payload(metric_name, value, tags, timestamp)
        self.deferred_metrics.append(payload)

    def write_deferred(self, timeout=None):
        """
        Writes all deferred metrics to kairosdb.

        :return: None
        :rtype: None
        """
        if self.deferred_metrics:
            response = self.requests.post(
                self.kairosdb_url,
                data=json.dumps(self.deferred_metrics),
                timeout=timeout or self.timeout
            )

            if 300 > response.status_code > 199:
                self.deferred_metrics = []

            if not self.fail_silently:
                handle_request_errors(response)

    def _construct_payload(self, metric_name, value, tags, timestamp=None):
        """
        Constructs a metric payload.

        :param metric_name: The name of the metric.
        :type metric_name: str
        :param value: The value of the metric.
        :type value: int
        :param tags: Tags to add to the metric.
        :type tags: dict
        :param timestamp: The time to register the metric. (Default: now)
        :type timestamp: datetime.datetime
        :return: A payload dictionary.
        :rtype: dict
        """
        ts = timestamp if timestamp else datetime.datetime.utcnow()
        payload = {
            'name': metric_name,
            'timestamp': self._datetime_to_millis(ts),
            'value': int(value),
            'tags': tags,
        }

        return payload

    @staticmethod
    def _datetime_to_millis(dt):
        """
        Converts a datetime object to timestamp in milliseconds.

        :param dt: The datetime object.
        :type dt: datetime.datetime
        :return: The timestamp in millis.
        :rtype: int
        """
        return int((dt - EPOCH).total_seconds() * 1000)
