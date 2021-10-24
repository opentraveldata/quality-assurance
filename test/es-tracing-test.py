#!/usr/bin/env python3

# https://github.com/opentracing-contrib/python-elasticsearch
# Note: opentracing apparently requires futures, which does not work
# on Python 3 (it is a backport on Python 2). A way to make it work is
# to require, in the Pipfile:
# futures = "==3.1.1"
import elasticsearch_opentracing

elasticsearch_opentracing.init_tracing(tracer) # An OpenTracing compatible tracer.
es = Elasticsearch(transport_class=elasticsearch_opentracing.TracingTransport)

elasticsearch_opentracing.set_active_span(main_span) # Optional.

es.index(index='test-index', doc_type='tweet', id=99, body={
    'author': 'linus',
    'text': 'Hello there',
    'timestamp': datetime.now(),
})
res = es.get(index='test-index', doc_type='tweet', id=99)

elasticsearch_opentracing.clear_active_span()

