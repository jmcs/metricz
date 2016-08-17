#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import requests
from clickclick import AliasedGroup, fatal_error
from environmental import Str
from metricz import MetricWriter

main = AliasedGroup(context_settings=dict(help_option_names=['-h', '--help']))


class Configuration:
    token_url = Str('OAUTH2_ACCESS_TOKEN_URL')
    credentials_dir = Str('CREDENTIALS_DIR', '/meta/credentials')


def parse_tags(ctx, param, value):
    tags = {}
    for tag in value:
        if '=' in tag:
            tag_name, value = tag.split('=', 1)
            tags[tag_name] = value
        else:
            raise click.UsageError(
                'Invalid tag {}. Tags should be in the form of key=value'.format(tag))
    return tags


@main.command()
@click.argument('metric_name')
@click.argument('value', type=int)
@click.argument('tags', nargs=-1, callback=parse_tags)
def write(metric_name: str, value: int, tags: dict):
    config = Configuration()
    try:
        token_url = config.token_url
    except AttributeError:
        fatal_error('Environment variable OAUTH2_ACCESS_TOKEN_URL is not set.')

    metric_writer = MetricWriter(
        token_url,
        config.credentials_dir,
        fail_silently=False
    )
    try:
        metric_writer.write_metric(metric_name, value, tags)
    except requests.ConnectionError as e:
        reason = e.args[0].reason   # type: requests.packages.urllib3.exceptions.NewConnectionError
        _, pretty_reason = str(reason).split(':', 1)
        fatal_error(pretty_reason)
    except requests.HTTPError as e:
        fatal_error('HTTP {}'.format(e.response.status_code))
