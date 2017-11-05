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
      <span>Interval: {{ disc_scanner.interval_sec }}s </span><br>
      <span>Next run time: {{ disc_scanner.next_run_time }} </span>
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      timer: null,
      subtitle_downloader: {
        active: 0,
      },
      disc_scanner: {
        active: 0,
        next_run_time: null,
        interval_sec: 0,
      },
    }
  },

  methods: {
    // Function to filter units
    fetchStatus: function () {
      this.axios.get('/api/v1/tasks/status/', {})
        .then(response => {
          this.subtitle_downloader.active = response.data.subtitle_downloader.active
          // this.disc_scanner.active = response.data.subtitle_downloader.active
          this.disc_scanner.next_run_time = response.data.disc_scanner.next_run_time.substring(0, 19).replace('T', ' ')
          this.disc_scanner.interval_sec = response.data.disc_scanner.interval_sec
        })
        .catch(error => {
          console.log(error)
        })
    },

    cancelAutoUpdate: function () {
      clearInterval(this.timer)
    }
  },
  created: function () {
    this.fetchStatus()
    this.timer = setInterval(this.fetchStatus, 1000)
  },
  beforeDestroy: function () {
    this.cancelAutoUpdate()
  }
}
</script>

<style>
</style>
