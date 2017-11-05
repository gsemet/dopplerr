# coding: utf-8

import dopplerr.api.v1.config
import dopplerr.api.v1.events
import dopplerr.api.v1.medias
import dopplerr.api.v1.notify
import dopplerr.api.v1.series
import dopplerr.api.v1.status


def add_api_blueprints(app):
    app.blueprint(dopplerr.api.v1.config.bp)
    app.blueprint(dopplerr.api.v1.events.bp)
    app.blueprint(dopplerr.api.v1.medias.bp)
    app.blueprint(dopplerr.api.v1.notify.bp)
    app.blueprint(dopplerr.api.v1.series.bp)
    app.blueprint(dopplerr.api.v1.status.bp)
