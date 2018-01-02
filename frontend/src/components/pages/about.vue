<template>
  <div class="content layout-padding">
    <div class="row">
      <q-card class="col-md">
        <q-card-title>About Dopplerr</q-card-title>
        <q-card-main>
          <table class="q-table">
            <tbody>
              <tr>
                <td><strong>Dopplerr</strong></td>
                <td>{{ version.dopplerr }}</td>
              </tr>
              <tr>
                <td><strong>Python</strong></td>
                <td>{{ version.python }}</td>
              </tr>
              <tr>
                <td><strong>Sanic</strong></td>
                <td>{{ version.sanic }}</td>
              </tr>
              <tr>
                <td><strong>App dir</strong></td>
                <td>{{ config.configdir }}</td>
              </tr>
              <tr>
                <td><strong>Media dir</strong></td>
                <td>{{ config.basedir }}</td>
              </tr>
            </tbody>
          </table>
        </q-card-main>
      </q-card>
      <q-card class="col-md">
        <q-card-title>More information</q-card-title>
        <q-card-main>
          <table class="q-table">
            <tbody>
              <tr>
                <td><strong>Support</strong></td>
                <td><a href="https://discordapp.com/channels/378849537520959510/378849838751678465">Discord rooms</a></td>
              </tr>
              <tr>
                <td><strong>Sources</strong></td>
                <td><a href="https://github.com/gsemet/dopplerr">Dopplerr on GitHub</a></td>
              </tr>
              <tr>
                <td><strong>Feature Requests</strong></td>
                <td><a href="http://feathub.com/gsemet/dopplerr">Vote on FeatHub</a></td>
              </tr>
            </tbody>
          </table>
        </q-card-main>
      </q-card>
    </div>
  </div>
</template>

<script>
import {
  QCard,
  QCardMain,
  QCardMedia,
  QCardSeparator,
  QCardTitle,
} from 'quasar'

export default {
  components: {
    QCard,
    QCardMain,
    QCardMedia,
    QCardSeparator,
    QCardTitle,
  },
  data () {
    return {
      version: '',
      config: '',
    }
  },

  methods: {
    // Function to filter units
    fetch: function () {
      this.axios.get('/api/v1/versions', {})
        .then(response => {
          this.version = response.data
        })
        .catch(error => {
          console.log(error)
        })
      this.axios.get('/api/v1/config/general/dirs', {})
        .then(response => {
          this.config = response.data
        })
        .catch(error => {
          console.log(error)
        })
    },
  },
  created: function () {
    this.fetch()
  },
}
</script>

<style>
</style>
