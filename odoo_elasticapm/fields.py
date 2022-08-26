from odoo_elasticapm.base import build_params, capture_exception, elasticapm

try:
    from odoo.fields import Field, Id, One2many
except ImportError:
    from openerp.fields import Field, Id, One2many

ori_field_get = Field.__get__
ori_id_get = Id.__get__
ori_one2many_get = One2many.__get__


def field_get(self, obj, owner):
    with elasticapm.capture_span(**build_params(self, "__get__")):
        try:
            return ori_field_get(self, obj, owner)
        except Exception as e:
            capture_exception(e)
            raise


def id_get(self, obj, owner):
    with elasticapm.capture_span(**build_params(self, "__get__")):
        try:
            return ori_id_get(self, obj, owner)
        except Exception as e:
            capture_exception(e)
            raise


def one2many_get(self, obj, owner):
    with elasticapm.capture_span(**build_params(self, "__get__")):
        try:
            return ori_one2many_get(self, obj, owner)
        except Exception as e:
            capture_exception(e)
            raise


Field.__get__ = field_get
# Id.__get__ = id_get
# One2many.__get__ = one2many_get
