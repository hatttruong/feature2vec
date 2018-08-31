<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Items">
        <div slot="content">
          <div v-for="item in items" :key="item.id">
            {{item.label}}
            {{item.id}}
            {{item.dbsource}}
            {{item.linksto}}
          </div>
        </div>
      </panel>
    </v-flex>
  </v-layout>
</template>
<script>
import Panel from '@/components/Panel'
import ItemService from '@/services/ItemsService'

export default {
  name: 'Items',
  components: {
    Panel
  },
  data () {
    return {
      items: null
    }
  },
  async mounted () {
    this.items = (await ItemService.index()).data
    console.log('items', this.items)
  }
}
</script>

<style scoped>

</style>
