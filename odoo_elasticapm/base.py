# -*- coding: utf-8 -*-


import os

try:
    from odoo.tools.config import config
    from odoo.http import request
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


def capture_exception(exception):
    handled = False
    for exception_class in EXCEPTIONS:
        if isinstance(exception, exception_class):
            handled = True
    elasticapm.label(
        exception_source="request",
        exception_type=type(exception).__name__,
        exception_handled=handled,
    )
    elastic_apm_client.capture_exception(
        context={"request": get_data_from_request()}, handled=handled
    )


if os.environ.get("ELASTIC_APM_ENVIRONMENT"):
    environment = os.environ.get("ELASTIC_APM_ENVIRONMENT")
else:
    environment = config.get("running_env")

elasticapm.instrument()

elastic_apm_client = elasticapm.Client(
    framework_name="Odoo",
    framework_version=odoo_version,
    service_name=os.environ.get("ELASTIC_APM_SERVICE_NAME", "Odoo"),
    environment=environment,
)
