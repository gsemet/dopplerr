<template>
  <div>
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
          filter: false
        },
        {
          label: 'Season',
          field: 'season_number',
          width: '40px',
          filter: false
        },
        {
          label: 'Episode',
          field: 'episode_number',
          width: '40px',
          filter: false
        },
        {
          label: 'Title',
          field: 'episode_title',
          width: '60px',
          filter: false
        },
        {
          label: 'Fetched Subtitles',
          field: 'subtitles_languages',
          width: '60px',
          filter: false
        }
      ]
    }
  },

  methods: {
    // Function to filter units
    fetchSeries: function () {
      this.axios.get('/api/v1/medias/series', {})
        .then(response => {
          this.medias = response.data.medias
        })
        .catch(error => {
          console.log(error)
        })
    }
  },

  beforeMount () {
    this.fetchSeries()
  }
}
</script>

<style>
</style>
