# coding: utf-8

import dopplerr.api.v1.events
import dopplerr.api.v1.series
import dopplerr.api.v1.other


def add_api_blueprints(app):
    app.blueprint(dopplerr.api.v1.events.bp)
    app.blueprint(dopplerr.api.v1.series.bp)
    app.blueprint(dopplerr.api.v1.other.bp)
