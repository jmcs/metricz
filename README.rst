===============================
Metricz
===============================

Metricz makes it easy to write your metrics to the Bus kairosdb instance.


Features
--------

* OAuth2 support.
* Option to batch write metrics at a later time.

Usage
-----

To simply write a metric:

.. code-block:: python

    from metricz import MetricWriter

    mw = MetricWriter(directory='/path/to/credentials/dir)

    mw.write_metric('some.metric.name', 123, {'some': 'tag'})

To write a metric with a custom timestamp:

.. code-block:: python

    import datetime

    # Make sure this is in UTC.
    timestamp = datetime.datetime(1981, 10, 26, 6, 24)

    mw.write_metric('some.metric.name', 34, {'some': 'tag'}, timestamp)


To batch write metrics:

.. code-block:: python

    # These are NOT written directly.
    mw.defer_metric('some.metric.name', 42, {'some': 'tag'})
    mw.defer_metric('some.other.metric.name', 64, {'some': 'tag'})
    mw.defer_metric('some.other.metric.name', 64, {'some': 'tag'})

    # Write all deferred metrics at once.
    mw.write_deferred()

TODO
----

* Retry on failure.
* Look at non-blocking options to write.
