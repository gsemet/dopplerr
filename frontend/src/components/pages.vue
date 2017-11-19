<template>
  <q-layout
    ref="layout"
    view="hHh Lpr lFf"
  >
    <q-toolbar
      slot="header"
      color="primary"
      glossy
    >
      <q-btn
        flat
        @click="$refs.layout.toggleLeft()"
      >
        <q-icon name="menu" />
      </q-btn>

      <!-- Navigation -->
      <q-tabs
        slot="navigation"
        color="primary"
        glossy
        >
        <q-route-tab
          icon="home"
          to="/home"
          replace
          slot="title"
          label="Home"
        />
        <q-route-tab
          icon="live tv"
          to="/series"
          replace
          slot="title"
          label="Series"
        />
      </q-tabs>

      <q-toolbar-title align="right">
        Dopplerr
        <div slot="subtitle">{{ version }}</div>
      </q-toolbar-title>

    </q-toolbar>

    <!-- Left Side Panel -->

    <div
      slot="left"
    >
      <q-list
        no-border
        link
        inset-separator
      >
        <q-list-header>Advanced Options</q-list-header>
        <!-- <q-side-link item to="/home">
          <q-item-side icon="school" />
          <q-item-main label="Home" sublabel="Overview" />
        </q-side-link> -->
        <!--
        <q-side-link item to="/movies">
          <q-item-side icon="school" />
          <q-item-main label="Movies" sublabel="Sonarr Films and Saga" />
        </q-side-link>
        -->
        <!-- <q-side-link item to="/series">
          <q-item-side icon="record_voice_over" />
          <q-item-main label="TV Series" sublabel="Series and Animes" />
        </q-side-link> -->
        <q-side-link item to="/events">
          <q-item-side icon="chat" />
          <q-item-main label="Events" sublabel="Main events" />
        </q-side-link>
        <q-side-link item to="/status">
          <q-item-side icon="fa-heartbeat" />
          <q-item-main label="Status" sublabel="Dopplerr backend status" />
        </q-side-link>
        <q-side-link item to="/logs">
          <q-item-side icon="fa-list" />
          <q-item-main label="Logs" sublabel="Debug logs" />
        </q-side-link>
        <q-side-link item to="/about">
          <q-item-side icon="fa-info-circle" />
          <q-item-main label="About Dopplerr"/>
        </q-side-link>
      </q-list>
    </div>
    <!-- Right Side Panel -->
    <!-- <div slot="right">
      Right Side of Layout
    </div> -->

    <!-- sub-routes get injected here: -->
    <div class="layout-page justify-center">
      <div>
        <router-view />
      </div>
    </div>

    <!-- Footer -->
    <!-- <q-toolbar slot="footer">
      <q-toolbar-title>
        Layout Footer
      </q-toolbar-title>
    </q-toolbar> -->
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
  QTab,
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
    QTab,
    QRouteTab
  },
  data () {
    return {
      version: ''
    }
  },
  methods: {
    // Function to filter units
    fetchVersion: function () {
      this.axios.get('/api/v1/version', {})
        .then(response => {
          this.version = response.data
        })
        .catch(error => {
          console.log(error)
        })
    }
  },
  mounted () {
    this.$refs.layout.hideLeft()
  },
  beforeMount () {
    this.fetchVersion()
  },
  beforeDestroy () {
  }
}
</script>

<style lang="stylus">
</style>
