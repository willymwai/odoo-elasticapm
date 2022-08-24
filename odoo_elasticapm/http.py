# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, elasticapm, capture_exception

try:
    from odoo.http import WebRequest, request


except ImportError:
    from openerp.http import WebRequest, request


ori_handle_exception = WebRequest._handle_exception


def _handle_exception(self, exception):
    capture_exception(exception)
    return ori_handle_exception(self, exception)


WebRequest._handle_exception = _handle_exception
