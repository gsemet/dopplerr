<template>
  <div>
    <q-data-table
      :data="events.events"
      :columns="columns"
    >
    <!-- :config="config"
    :columns="columns"
    @refresh="refresh" -->
  </q-data-table>
  </div>
</template>

<script>
import {
  QDataTable
} from 'quasar'

export default {
  components: {
    QDataTable
  },

  data () {
    return {
      events: [],
      columns: [
        {
          label: 'Date',
          field: 'timestamp',
          width: '80px',
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
          width: '80px',
          filter: true
        },
        {
          label: 'Message',
          field: 'message',
          width: '200px',
          filter: true
        }
      ]
    }
  },

  methods: {
    // Function to filter units
    fetchRecentEvents: function () {
      this.axios.get('/api/v1/events/recent', {})
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
