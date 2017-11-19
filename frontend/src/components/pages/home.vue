<template>
  <div>
    <div
      class="q-parallax"
      style="height: 200px;"
    >
      <div
        class="q-parallax-image absolute-full"
      >
        <img
          src="/statics/hubblecast43f-thin.png"
          class="ready"
          style="transform: translate3d(-50%, 0px, 0px);"
         >
      </div>
      <div
        class="q-parallax-text absolute-full column flex-center"
      >
        <h1>Dopplerr</h1>
        <p>Subtitle Synchronizer</p>
      </div>
    </div>
    <div class="content layout-padding">
      <div class="row">
        <q-card class="col">
          <q-card-title>Recent Events</q-card-title>
          <q-card-main>
            <q-data-table
              :data="events"
              :columns="recent_events_table_cfg.columns"
              :config="recent_events_table_cfg.config"
            >
            </q-data-table>
          </q-card-main>
        </q-card>
        <q-card class="col">
          <q-card-title>Recent Fetched Series Subtitles</q-card-title>
          <q-card-main>
            <q-data-table
              :data="fetched_episodes"
              :columns="recent_episodes_table_cfg.columns"
              :config="recent_episodes_table_cfg.config"
            >
            </q-data-table>
          </q-card-main>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script>
import {
  QBtn,
  QCard,
  QCardActions,
  QCardMain,
  QCardMedia,
  QCardSeparator,
  QCardTitle,
  QDataTable,
  QIcon,
} from 'quasar'

export default {
  components: {
    QBtn,
    QCard,
    QCardActions,
    QCardMain,
    QCardMedia,
    QCardSeparator,
    QCardTitle,
    QDataTable,
    QIcon,
  },

  data () {
    return {
      timer: null,
      events: [],
      fetched_episodes: [],
      recent_events_table_cfg: {
        config: {
          rowHeight: '30px',
          noHeader: true,
          pagination: {
            rowsPerPage: 5,
            options: [5, 10, 20, 50]
          }
        },
        columns: [
          {
            label: 'Date',
            field: 'timestamp',
            width: '80px',
            filter: false,
            sort (a, b) {
              return (new Date(a)) - (new Date(b))
            },
            type: 'string',
            format (value, row) {
              return new Date(value).toLocaleString()
            },
          },
          {
            label: 'Message',
            field: 'message',
            width: '200px',
            filter: false
          }
        ]
      },
      recent_episodes_table_cfg: {
        config: {
          rowHeight: '30px',
          noHeader: false,
          pagination: {
            rowsPerPage: 5,
            options: [5, 10, 20, 50]
          }
        },
        columns: [
          {
            label: 'Date',
            field: 'added_timestamp',
            width: '80px',
            filter: false,
            sort (a, b) {
              return (new Date(a)) - (new Date(b))
            },
            type: 'string',
            format (value, row) {
              return new Date(value).toLocaleString()
            },
          },
          {
            label: 'Series',
            field: 'series_title',
            width: '80px',
            filter: false
          },
          {
            label: 'Season',
            field: 'season_number',
            width: '30px',
            filter: false
          },
          {
            label: 'Episode',
            field: 'episode_number',
            width: '30px',
            filter: false
          },
          {
            label: 'Title',
            field: 'episode_title',
            width: '40px',
            filter: false
          },
          {
            label: 'Subtitles',
            field: 'subtitle_language',
            width: '40px',
            filter: false,
          },
        ]
      }
    }
  },

  methods: {
    // Function to filter units
    fetch: function () {
      this.axios.get('/api/v1/recent/events/50', {})
        .then(response => {
          this.events = response.data.events
        })
        .catch(error => {
          console.log(error)
        })
      this.axios.get('/api/v1/recent/series/50', {})
        .then(response => {
          this.fetched_episodes = response.data.events
        })
        .catch(error => {
          console.log(error)
        })
    },

    cancelAutoUpdate: function () {
      clearInterval(this.timer)
    }
  },

  beforeMount () {
    this.fetch()
    this.timer = setInterval(this.fetch, 5000)
  },
  beforeDestroy: function () {
    this.cancelAutoUpdate()
  }

}
</script>

<style>
</style>
