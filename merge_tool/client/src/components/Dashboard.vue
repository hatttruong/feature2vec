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

export default {
  name: 'Dashboard',
  data () {
    return {
      totalItems: 1000,
      processedItems: 0,
      autoConcepts: 1000,
      processedConcepts: 0
    }
  },
  components: {
    Panel
  }
}
</script>

<style scoped>

</style>
