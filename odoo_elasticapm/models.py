# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .base import elasticapm, version_older_then, capture_exception

try:
    from odoo import api, models
    from odoo.exceptions import UserError
except ImportError:
    from openerp import api, models
    from openerp.exceptions import UserError


def build_params(self, method):
    return {
        "name": "ORM {} {}".format(self._name, method),
        "span_type": "odoo",
        "span_subtype": "orm",
        "extra": {
            "odoo": {
                "class": self._name,
                "method": method,
                "nbr_record": hasattr(self, "_ids") and len(self) or 0,
            }
        },
    }


BaseModel = models.BaseModel
ori_create = BaseModel.create
ori_write = BaseModel.write
ori_search = BaseModel._search
ori_browse = BaseModel.browse
ori_unlink = BaseModel.unlink


def write(self, vals):
    with elasticapm.capture_span(**build_params(self, "write")):
        try:
            return ori_write(self, vals)
        except Exception as e:
            capture_exception(e)
            raise


@api.returns("self", lambda value: value.id)
def create(self, vals):
    with elasticapm.capture_span(**build_params(self, "create")):
        try:
            return ori_create(self, vals)
        except Exception as e:
            capture_exception(e)
            raise


def _search(self, *args, **kwargs):
    with elasticapm.capture_span(**build_params(self, "search")):
        try:
            return ori_search(self, *args, **kwargs)
        except Exception as e:
            capture_exception(e)
            raise


def browse(self, *args, **kwargs):
    with elasticapm.capture_span(**build_params(self, "browse")):
        try:
            return ori_browse(self, *args, **kwargs)
        except Exception as e:
            capture_exception(e)
            raise


def unlink(self):
    with elasticapm.capture_span(**build_params(self, "unlink")):
        try:
            return ori_unlink(self)
        except Exception as e:
            capture_exception(e)
            raise


if version_older_then("13.0"):
    unlink = api.multi(unlink)
    write = api.multi(write)

if version_older_then("12.0"):
    create = api.model(create)
else:
    create = api.model_create_multi(create)

if version_older_then("10.0"):
    _search = api.cr_uid_context(_search)
else:
    _search = api.model(_search)

BaseModel.create = create
BaseModel.write = write
BaseModel._search = _search
BaseModel.browse = browse
BaseModel.unlink = unlink
