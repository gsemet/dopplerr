<template>
  <div class="flex-row-docs">
    <h4>Latest Events</h4>
    <div class="doc-container">
      <q-data-table
        :data="events.events"
        :columns="recent_events_table_cfg.columns"
        :config="recent_events_table_cfg.config"
      >
      </q-data-table>
    </div>
    <!-- <h4>Recent fetch</h4> -->
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
      }
    }
  },

  methods: {
    // Function to filter units
    fetchRecentEvents: function () {
      this.axios.get('/api/v1/events/recent/5', {})
        .then(response => {
          this.events = response.data
        })
        .catch(error => {
          console.log(error)
        })
    }
  },

  beforeMount () {
    this.fetchRecentEvents()
  }

}
</script>

<style>
</style>
