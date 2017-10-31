<template>
  <div class="flex-row-docs">
    <h4>Recent Events</h4>
    <div class="doc-container">
      <q-data-table
        :data="events"
        :columns="recent_events_table_cfg.columns"
        :config="recent_events_table_cfg.config"
      >
      </q-data-table>
    </div>
    <h4>Recent Fetched Series Subtitles</h4>
    <div class="doc-container">
      <q-data-table
        :data="fetched_episodes"
        :columns="recent_episodes_table_cfg.columns"
        :config="recent_episodes_table_cfg.config"
      >
      </q-data-table>
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
      events: [],
      fetched_episodes: [],
      recent_events_table_cfg: {
        config: {
          rowHeight: '30px',
          noHeader: true,
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
      this.axios.get('/api/v1/recent/events/5', {})
        .then(response => {
          this.events = response.data.events
        })
        .catch(error => {
          console.log(error)
        })
      this.axios.get('/api/v1/recent/fetched/series/5', {})
        .then(response => {
          this.fetched_episodes = response.data.events
        })
        .catch(error => {
          console.log(error)
        })
    }
  },

  beforeMount () {
    this.fetch()
  }

}
</script>

<style>
</style>
