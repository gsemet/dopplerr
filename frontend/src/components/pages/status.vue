<template>
  <div class="content layout-padding">
    <div class="row">
      <q-card class="col">
        <q-card-title>Subtitle Download</q-card-title>
        <q-card-main>
          <span
            v-if="subtitle_downloader.active === 1"
          >
            State: Active
            <i
              class="material-icons text-negative"
              style="font-size: 22px">info
            </i>
          </span>
          <span
            v-else-if ="subtitle_downloader.active === 0"
          >
            State: Inactive
            <i
              class="material-icons text-positive"
              style="font-size: 22px">info
            </i>
          </span>
        </q-card-main>
      </q-card>
    </div>
    <div class="row">
      <q-card class="col">
        <q-card-title>Disc Scanner</q-card-title>
        <q-card-main>
          <table class="q-table">
            <tbody>
              <tr v-if="disc_scanner.started === 0">
                <td><strong>State</strong></td>
                <td>Not enabled</td>
                <td></td>
              </tr>
              <tr v-if="disc_scanner.started === 1">
                <td><strong>State</strong></td>
                <td>
                  <span
                    v-if="disc_scanner.active === 1"
                  >
                    Active
                    <i
                      class="material-icons text-negative"
                      style="font-size: 22px">info
                    </i>
                  </span>
                  <span
                    v-else
                  >
                    Inactive
                    <i
                      class="material-icons text-positive"
                      style="font-size: 22px">info
                    </i>
                  </span>
                </td>
                <td></td>
              </tr>
              <tr v-if="disc_scanner.started === 1">
                <td><strong>Interval</strong></td>
                <td>
                  <span>{{ disc_scanner.interval_hours }} hour</span><span
                    v-if="disc_scanner.interval_hours > 0">s</span>
                </td>
                <td></td>
              </tr>
              <tr v-if="disc_scanner.started === 1">
                <td><strong>Next run time</strong></td>
                <td>{{ disc_scanner.next_run_time }}</td>
                <td>
                  <q-btn
                      icon="fa-refresh"
                      flat
                      small
                      :disable="disc_scanner.active == 1"
                      @click="force_disc_scanner_start()"
                    >
                    Refresh
                  </q-btn>
                </td>
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
  QBtn,
  QIcon,
  QCard,
  QCardMain,
  QCardMedia,
  QCardSeparator,
  QCardTitle,
} from 'quasar'

export default {
  components: {
    QBtn,
    QIcon,
    QCard,
    QCardMain,
    QCardMedia,
    QCardSeparator,
    QCardTitle,
  },
  data () {
    return {
      timer: null,
      subtitle_downloader: {
        active: 0,
      },
      disc_scanner: {
        active: 0,
        started: 0,
        next_run_time: null,
        interval_hours: 0,
      },
    }
  },

  methods: {
    // Function to filter units
    fetch: function () {
      this.axios.get('/api/v1/tasks/status/', {})
        .then(response => {
          this.subtitle_downloader = response.data.subtitle_downloader
          this.disc_scanner = response.data.disc_scanner
          this.disc_scanner.next_run_time = response.data.disc_scanner.next_run_time.substring(0, 19).replace('T', ' ')
        })
        .catch(error => {
          console.log(error)
        })
    },

    cancelAutoUpdate: function () {
      clearInterval(this.timer)
    },

    force_disc_scanner_start: function () {
      this.disc_scanner.active = 1
      this.axios.post('/api/v1/tasks/scanner/start')
    }
  },
  created: function () {
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
