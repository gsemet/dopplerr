<template>
  <div>
    <h4>Recent Logs</h4>
    <q-data-table
      :data="logs"
      :columns="columns"
      :config="config"
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
      timer: null,
      logs: [],
      config: {
        pagination: {
          rowsPerPage: 30,
          options: [30, 100, 200, 500]
        }
      },
      columns: [
        {
          label: 'Date',
          field: 'timestamp',
          width: '80px',
          filter: false,
        },
        {
          label: 'Level',
          field: 'level',
          width: '30px',
          filter: true
        },
        {
          label: 'Logger',
          field: 'logger',
          width: '30px',
          filter: true
        },
        {
          label: 'Message',
          field: 'message',
          width: '200px',
          filter: true,
          type: 'string',
          format (value, row) {
            return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          }
        }
      ]
    }
  },

  methods: {
    // Function to filter units
    fetch: function () {
      this.axios.get('/api/v1/logs?limit=100', {})
        .then(response => {
          this.logs = response.data
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
    this.timer = setInterval(this.fetch, 3000)
  },
  beforeDestroy: function () {
    this.cancelAutoUpdate()
  }
}
</script>

<style>
</style>
