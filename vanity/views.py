# -*- coding: utf-8 -*-
"""
    vanity.views
    ~~~~~~~~~~~~

    This module contains the views for the
    vanity Plugin.

    :copyright: (c) 2018 by Михаил Лебедев.
    :license: BSD License, see LICENSE for more details.
"""
from flask import Blueprint, flash
from flask_babelplus import gettext as _

from flaskbb.utils.helpers import render_template
from flaskbb.plugins.models import PluginRegistry


vanity_bp = Blueprint("vanity_bp", __name__, template_folder="templates")


@vanity_bp.route("/")
def index():
    plugin = PluginRegistry.query.filter_by(name="vanity").first()
    if plugin and not plugin.is_installed:
        flash(_("Plugin is not installed."), "warning")

    return render_template("index.html", plugin=plugin)
