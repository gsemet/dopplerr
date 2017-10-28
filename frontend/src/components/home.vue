<template>
  <q-layout
    ref="layout"
    view="lHh Lpr fff"
    :left-class="{'bg-grey-2': true}"
  >
    <q-toolbar slot="header">
      <q-btn
        flat
        @click="$refs.layout.toggleLeft()"
      >
        <q-icon name="menu" />
      </q-btn>

      <q-toolbar-title>
        Dopplerr
        <div slot="subtitle">version {{$q.version}}</div>
      </q-toolbar-title>
    </q-toolbar>

    <!-- Navigation -->
    <!-- <q-tabs slot="navigation">
      <q-route-tab slot="title" icon="view_quilt" to="/status" replace hide="icon" label="Status" />
      <q-route-tab slot="title" icon="view_day" to="/events" replace hide="icon" label="Events" />
    </q-tabs> -->

    <!-- Left Side Panel -->
    <div slot="left">
      <q-list no-border link inset-separator>
        <q-list-header>Dopplerr</q-list-header>
        <q-side-link item to="/home">
          <q-item-side icon="school" />
          <q-item-main label="Home" sublabel="Overview" />
        </q-side-link>
        <!-- <q-side-link item to="/movies">
          <q-item-side icon="school" />
          <q-item-main label="Movies" sublabel="Sonarr Films and Saga" />
        </q-side-link>
        <q-side-link item to="/series">
          <q-item-side icon="record_voice_over" />
          <q-item-main label="TV Series" sublabel="Radarr Series and Animes" />
        </q-side-link> -->
        <q-side-link item to="/events">
          <q-item-side icon="chat" />
          <q-item-main label="Events" sublabel="" />
        </q-side-link>
        <!-- <q-side-link item to="/status">
          <q-item-side icon="rss feed" />
          <q-item-main label="Status" sublabel="" />
        </q-side-link> -->
      </q-list>
    </div>
    <!-- Right Side Panel -->
    <div slot="right">
      Right Side of Layout
    </div>
    <!-- sub-routes get injected here: -->
    <router-view />
    <!-- Footer -->
    <q-toolbar slot="footer">
      <q-toolbar-title>
        Layout Footer
      </q-toolbar-title>
    </q-toolbar>
  </q-layout>
</template>

<script>
import {
  QLayout,
  QToolbar,
  QToolbarTitle,
  QBtn,
  QIcon,
  QList,
  QListHeader,
  QItem,
  QItemSide,
  QItemMain,
  QSideLink,
  QTabs,
  QRouteTab
} from 'quasar'

export default {
  name: 'index',
  components: {
    QLayout,
    QToolbar,
    QToolbarTitle,
    QBtn,
    QIcon,
    QList,
    QListHeader,
    QItem,
    QItemSide,
    QItemMain,
    QSideLink,
    QTabs,
    QRouteTab
  },
  data () {},
  mounted () {
  },
  beforeDestroy () {
  }
}
</script>

<style lang="stylus">
</style>
