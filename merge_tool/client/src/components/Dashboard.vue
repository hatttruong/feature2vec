<template>
  <v-layout row>
    <v-flex xs6 offset-xs3>
      <panel title="Dashboard">
        <div slot="content">
          <h2>Total Items: <b>{{totalItems}}</b></h2>
          <h2>Processed Items: <b>{{processedItems}}</b></h2>
          <h2>Remaining Items: <b>{{totalItems - processedItems}}</b></h2>
          <br>
          <hr><br>
          <h2>Auto Concepts: <b>{{autoConcepts}}</b></h2>
          <h2>Processed Concepts: <b>{{processedConcepts}}</b></h2>
        </div>
      </panel>
    </v-flex>
  </v-layout>
</template>

<script>
import Panel from '@/components/Panel'
import ConceptsService from '@/services/ConceptsService'
import ItemService from '@/services/ItemsService'

export default {
  name: 'Dashboard',
  data () {
    return {
      totalItems: null,
      processedItems: null,
      autoConcepts: null,
      processedConcepts: null
    }
  },
  components: {
    Panel
  },
  async mounted () {
    // load all items which are not processed
    const items = (await ItemService.index()).data
    this.totalItems = items.length
    this.processedItems = items.filter(item => item.conceptid > 0).length

    // concepts
    const concepts = (await ConceptsService.index()).data
    this.autoConcepts = concepts.filter(concept => concept.created_by === 'SYS').length
    this.processedConcepts = concepts.filter(concept => concept.created_by === 'USER').length
  }
}
</script>

<style scoped>

</style>
