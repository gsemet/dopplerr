<template>
  <div>
    <div>
      <h4>Subtitle Download</h4>
      <span
        v-if="subtitle_downloader.active === 1"
      >
        Active
        <i
          class="material-icons text-negative"
          style="font-size: 22px">info
        </i>
      </span>
      <span
        v-else-if ="subtitle_downloader.active === 0"
      >
        Inactive
        <i
          class="material-icons text-positive"
          style="font-size: 22px">info
        </i>
      </span>
    </div>
    <div>
      <h4>Disc Scanner</h4>
      <div
        v-if="disc_scanner.started === 0"
      >
        Not enabled
      </div>
      <div v-else>
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
          v-else-if ="disc_scanner.active === 0"
        >
          Inactive
          <i
            class="material-icons text-positive"
            style="font-size: 22px">info
          </i>
        </span><br>
        <span>
          Interval: {{ disc_scanner.interval_hours }} hour<span
            v-if="disc_scanner.interval_hours > 0">s</span>
        </span><br>
        <span>Next run time: {{ disc_scanner.next_run_time }}</span>
        <span>
          <q-btn
            icon="fa-refresh"
            flat
            small
            :disable="disc_scanner.active"
            @click="force_disc_scanner_start()"
          >Refresh</q-btn>

        </span>
      </div>
    </div>
  </div>
</template>

<script>
import {
  QBtn,
  QIcon
} from 'quasar'

export default {
  components: {
    QBtn,
    QIcon
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
