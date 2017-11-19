<template>
  <div class="content layout-padding">
    <h4>Series</h4>
    <q-data-table
      :data="medias"
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
      timer: null,
      medias: [],
      columns: [
        {
          label: 'Added',
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
          filter: true
        },
        {
          label: 'Season',
          field: 'season_number',
          width: '40px',
          filter: true
        },
        {
          label: 'Episode',
          field: 'episode_number',
          width: '30px',
          filter: true
        },
        {
          label: 'Title',
          field: 'episode_title',
          width: '50px',
          filter: true
        },
        {
          label: 'Subtitles',
          field: 'subtitle_languages',
          width: '40px',
          filter: true,
          type: 'string',
          format (value, row) {
            if (value) {
              return value.join(', ')
            }
          },
        },
        {
          label: 'Dirty',
          field: 'dirty',
          width: '30px',
          filter: false,
          type: 'int',
        }
      ]
    }
  },

  methods: {
    // Function to filter units
    fetch: function () {
      this.axios.get('/api/v1/medias/series/all', {})
        .then(response => {
          this.medias = response.data.medias
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
