<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Concepts">
        <v-btn
          slot="action"
          @click="navigateTo({name: 'merge'})"
          class="blue accent-1"
          light small absolute right middle fab>
          <v-icon>add</v-icon>
        </v-btn>
        <div slot="content">
          <v-card flat>
            <v-data-table
              :headers="headers"
              :rows-per-page-items=[10,25,50,100]
              :items="concepts"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.conceptid }}</td>
                <td class="text-xs-left">{{ props.item.concept }}</td>
                <td class="text-xs-left">{{ props.item.linksto }}</td>
                <td>{{ props.item.isnumeric}}</td>
                <td class="text-xs-left">{{ props.item.created_by }}</td>
              </template>
            </v-data-table>
          </v-card>
        </div>
      </panel>
    </v-flex>
  </v-layout>
</template>

<script>
import Panel from '@/components/Panel'
import ConceptsService from '@/services/ConceptsService'

export default {
  name: 'Concepts',
  components: {
    Panel
  },
  data () {
    return {
      concepts: [],
      headers: [
        { text: 'Id', value: 'conceptid' },
        { text: 'Name', value: 'concept' },
        { text: 'Linksto', value: 'linksto' },
        { text: 'Numeric', value: 'isnumeric' },
        { text: 'Created By', value: 'created_by' }
      ]
    }
  },
  methods: {
    navigateTo (route) {
      this.$router.push(route)
    }
  },
  async mounted () {
    this.concepts = (await ConceptsService.index()).data
    console.log('Concepts', this.concepts)
  }
}
</script>

<style scoped>

</style>
