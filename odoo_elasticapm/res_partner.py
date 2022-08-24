from .base import base_write_create, version_older_then

try:
    from odoo import api
    from odoo.addons.base.models.res_partner import Partner
except ImportError:
    from openerp import api
    from openerp.addons.base.models.res_partner import Partner

ori_write = Partner.write
ori_create = Partner.create


def write(self, vals):
    return base_write_create(self, vals, ori_write, "write")


@api.returns("self", lambda value: value.id)
def create(self, vals):
    return base_write_create(self, vals, ori_create, "create")


if version_older_then("12.0"):
    create = api.model(create)
else:
    create = api.model_create_multi(create)


Partner.write = write
Partner.create = create
