import threading

import elasticapm

from odoo_elasticapm.base import build_params, capture_exception

ori_bootstrap_inner = threading.Thread._bootstrap_inner


def _bootstrap_inner(self):
    try:
        with elasticapm.capture_span(**build_params(self, "_bootstrap_inner")):
            return ori_bootstrap_inner(self)
    except Exception as e:
        capture_exception(e)
        raise


threading.Thread._bootstrap_inner = _bootstrap_inner
