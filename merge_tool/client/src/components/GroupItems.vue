<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Groups">
        <v-btn
          slot="action"
          @click="navigateTo({name: 'merge'})"
          class="blue accent-1"
          light small absolute right middle fab>
          <v-icon>add</v-icon>
        </v-btn>
        <div slot="content">
          <div v-for="group in groupItems" :key="group.id">
            {{item.label}}
          </div>
        </div>
      </panel>
    </v-flex>
  </v-layout>
</template>

<script>
import Panel from '@/components/Panel'
import GroupItemsService from '@/services/GroupItemsService'

export default {
  name: 'GroupItems',
  components: {
    Panel
  },
  data () {
    return {
      groupItems: null
    }
  },
  methods: {
    navigateTo (route) {
      this.$router.push(route)
    }
  },
  async mounted () {
    this.groupItems = (await GroupItemsService.index()).data
    console.log('groupItems', this.groupItems)
  }
}
</script>

<style scoped>

</style>
