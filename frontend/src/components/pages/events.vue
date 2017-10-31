<template>
  <div>
    <h4>Recent Events</h4>
    <q-data-table
      :data="events"
      :columns="columns"
    >
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
          width: '50px',
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
      this.axios.get('/api/v1/recent/events/100', {})
        .then(response => {
          this.events = response.data.events
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
