# -*- coding: utf-8 -*-


import os
import sys
import traceback

try:
    from odoo.tools.config import config
    from odoo.http import request
    from odoo import api
    import odoo
    from odoo.exceptions import (
        UserError,
        RedirectWarning,
        AccessDenied,
        AccessError,
        MissingError,
        ValidationError,
        except_orm,
    )
except ImportError:
    from openerp.tools.config import config
    from openerp.http import request
    from openerp import api
    import openerp as odoo
    from openerp.exceptions import (
        Warning as UserError,
        RedirectWarning,
        AccessDenied,
        AccessError,
        MissingError,
        ValidationError,
        except_orm,
    )

# The elasticapm lib must be imported just after odoo
# so the odoo.evented variable will be correctly defined

import elasticapm

odoo_version = odoo.release.version


def version_older_then(version):
    return (
        odoo.tools.parse_version(odoo_version)[0] < odoo.tools.parse_version(version)[0]
    )


EXCEPTIONS = [
    UserError,
    RedirectWarning,
    AccessDenied,
    AccessError,
    MissingError,
    ValidationError,
    except_orm,
]


def get_data_from_request():
    httprequest = request.httprequest
    data = {
        "headers": dict(**httprequest.headers),
        "method": httprequest.method,
        "socket": {
            "remote_address": httprequest.remote_addr,
            "encrypted": httprequest.scheme == "https",
        },
        "url": elasticapm.utils.get_url_dict(httprequest.url),
    }
    # remove Cookie header since the same data is in request["cookies"] as well
    data["headers"].pop("Cookie", None)
    return data


def capture_exception(exception, is_http_request=False):
    handled = False
    exc_info = sys.exc_info()
    message = ''.join(traceback.format_tb(exception.__traceback__))
    for exception_class in EXCEPTIONS:
        if isinstance(exception, exception_class):
            handled = True
    elasticapm.label(
        exception_source="request",
        exception_type=type(exception).__name__,
        exception_handled=handled,
    )
    if is_http_request:
        elastic_apm_client.capture_exception(
            context={"request": get_data_from_request()},
            handled=handled,
            exc_info=exc_info,
            message=message,
        )
    else:
        elastic_apm_client.capture_exception(
            handled=handled, exc_info=exc_info, message=message
        )


def build_params(self, method, span_type="ORM"):
    try:
        class_name = self._name
    except AttributeError:
        class_name = self.__class__.__name__
    return {
        "name": "{} {} {}".format(span_type, class_name, method),
        "span_type": "odoo",
        "span_subtype": "orm",
        "extra": {
            "odoo": {
                "class": class_name,
                "method": method,
                "nbr_record": hasattr(self, "_ids") and len(self) or 0,
            }
        },
    }


def base_write_create(self, vals, ori_method, method_name):
    try:
        with elasticapm.capture_span(**build_params(self, method_name)):
            return ori_method(self, vals)
    except Exception as e:
        capture_exception(e)
        raise


if os.environ.get("ELASTIC_APM_ENVIRONMENT"):
    environment = os.environ.get("ELASTIC_APM_ENVIRONMENT")
else:
    environment = config.get("running_env")

elastic_apm_client = elasticapm.Client(
    framework_name="Odoo",
    framework_version=odoo_version,
    service_name=os.environ.get("ELASTIC_APM_SERVICE_NAME", "Odoo"),
    environment=environment,
)

elasticapm.instrument()

elastic_apm_client.begin_transaction("Odoo")
