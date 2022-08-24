from odoo_elasticapm.base import build_params, capture_exception, elasticapm

try:
    from odoo.fields import Field, Id, One2many
except ImportError:
    from openerp.fields import Field, Id, One2many


for field in [Field, Id, One2many]:
    ori_get = field.__get__

    def __get__(self, obj, owner):
        if isinstance(self, field):
            with elasticapm.capture_span(**build_params(self, "__get__")):
                try:
                    return ori_get(self, obj, owner)
                except Exception as e:
                    capture_exception(e)
                    raise

    field.__get__ = __get__
