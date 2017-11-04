<template>
  <div>
    Subtitle Download:
    <span
      v-if="subtitle_downloader === 1"
    >
      Active
      <i
        class="material-icons text-negative"
        style="font-size: 22px">info
      </i>
    </span>
    <span
      v-else-if ="subtitle_downloader === 0"
    >
      Inactive
      <i
        class="material-icons text-positive"
        style="font-size: 22px">info
      </i>
    </span>
  </div>
</template>

<script>
export default {
  data () {
    return {
      timer: null,
      subtitle_downloader: null,
    }
  },

  methods: {
    // Function to filter units
    fetchStatus: function () {
      this.axios.get('/api/v1/tasks/status/', {})
        .then(response => {
          this.subtitle_downloader = response.data.subtitle_downloader.active
          console.log('fetched - ' + this.subtitle_downloader)
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
