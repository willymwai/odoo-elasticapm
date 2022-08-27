import threading

import elasticapm

from odoo_elasticapm.base import build_params, capture_exception

ori_start = threading.Thread.start
ori_run = threading.Thread.run


def start(self):
    try:
        with elasticapm.capture_span(**build_params(self, "start", span_type="thread")):
            return ori_start(self)
    except Exception as e:
        capture_exception(e)
        raise


def run(self):
    try:
        with elasticapm.capture_span(**build_params(self, "run", span_type="thread")):
            return ori_run(self)
    except Exception as e:
        capture_exception(e)
        raise


threading.Thread.start = start
threading.Thread.run = run
