<template>
  <div class="content layout-padding">
    <h4>Recent Logs</h4>
    <q-data-table
      :data="logs"
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
        columnPicker: true,
        pagination: {
          rowsPerPage: 50,
          options: [50, 100, 200, 500]
        },
      },
      columns: [
        {
          label: 'Date',
          field: 'timestamp',
          width: '50px',
          filter: false,
          type: 'string',
          format (value, row) {
            return value.slice(0, 19)
          },
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
          width: '50px',
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
.wrap-message {
  white-space: normal;
}
</style>
