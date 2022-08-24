from .base import base_write_create

try:
    from odoo import api
    from odoo.addons.base.models import res_partner as ResPartner
except ImportError:
    from openerp import api
    from openerp.addons.base.models import res_partner as ResPartner

ori_write = ResPartner.write
ori_create = ResPartner.create


def write(self, vals):
    return base_write_create(self, vals, ori_write, "write")


@api.returns("self", lambda value: value.id)
def create(self, vals):
    return base_write_create(self, vals, ori_create, "create")


ResPartner.write = write
ResPartner.create = create
