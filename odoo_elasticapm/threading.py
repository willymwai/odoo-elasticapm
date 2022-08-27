import threading

import elasticapm

from odoo_elasticapm.base import build_params, capture_exception

ori_run = threading.Thread.run


def run(self):
    try:
        with elasticapm.capture_span(**build_params(self, "run")):
            return ori_run(self)
    except Exception as e:
        capture_exception(e)
        raise


threading.Thread.run = run
