<template>
  <div class="content layout-padding">
    <h4>Recent Events</h4>
    <div>
      Click on this button to stop auto log refresh and load {{ manual_refresh_lines }} lines:
      <q-btn
        icon="fa-refresh"
        flat
        small
        @click="manual_refresh()"
      >Manual Refresh</q-btn>
    </div>
    <q-data-table
      :data="events"
      :columns="columns"
      :config="config"
    >
      <!-- Custom renderer for "message" column -->
      <template slot="col-message" slot-scope="cell">
        <span class="light-paragraph wrap-message">{{cell.data}}</span>
      </template>
    </q-data-table>
  </div>
</template>

<script>
import {
  QBtn,
  QDataTable,
} from 'quasar'

export default {
  components: {
    QBtn,
    QDataTable,
  },

  data () {
    return {
      timer: null,
      events: [],
      manual_refresh_lines: 10000,
      config: {
        columnPicker: true,
        pagination: {
          rowsPerPage: 30,
          options: [30, 100, 200, 500]
        }
      },
      columns: [
        {
          label: 'Date',
          field: 'timestamp',
          width: '70px',
          filter: true,
          sort (a, b) {
            return (new Date(a)) - (new Date(b))
          },
          type: 'string',
          format (value, row) {
            return new Date(value).toLocaleString()
          },
        },
        {
          label: 'Type',
          field: 'type',
          width: '50px',
          filter: true
        },
        {
          label: 'Message',
          field: 'message',
          width: '200px',
          filter: true,
        }
      ]
    }
  },

  methods: {
    // Function to filter units
    fetch: function (limit) {
      this.axios.get('/api/v1/recent/events/' + limit, {})
        .then(response => {
          this.events = response.data.events
        })
        .catch(error => {
          console.log(error)
        })
    },

    fetchAuto: function () {
      this.fetch(500)
    },

    manual_refresh: function () {
      this.cancelAutoUpdate()
      this.fetch(this.manual_refresh_lines)
    },

    cancelAutoUpdate: function () {
      clearInterval(this.timer)
    }
  },

  beforeMount () {
    this.fetchAuto()
    this.timer = setInterval(this.fetchAuto, 5000)
  },
  beforeDestroy: function () {
    this.cancelAutoUpdate()
  }
}
</script>

<style>
.wrap-message {
  white-space: normal;
}
</style>
