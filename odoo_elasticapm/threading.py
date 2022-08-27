import threading

import elasticapm

from odoo_elasticapm.base import build_params, capture_exception

ori_start = threading.Thread.start


def start(self):
    try:
        with elasticapm.capture_span(**build_params(self, "start")):
            return ori_start(self)
    except Exception as e:
        capture_exception(e)
        raise


threading.Thread.start = start
