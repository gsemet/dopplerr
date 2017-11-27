# coding: utf-8

# Dopplerr
import dopplerr.api.v1.config
import dopplerr.api.v1.events
import dopplerr.api.v1.medias
import dopplerr.api.v1.notify
import dopplerr.api.v1.series
import dopplerr.api.v1.status


def add_api_blueprints(app):
    for modu in [
            'config',
            'events',
            'medias',
            'notify',
            'series',
            'status',
    ]:
        modu = getattr(dopplerr.api.v1, modu)
        app.blueprint(modu.bp)
