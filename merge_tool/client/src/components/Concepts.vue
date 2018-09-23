<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Concepts">
        <v-btn
          slot="action"
          @click="navigateTo({name: 'concept', params: { conceptid: -1 }})"
          class="blue accent-1"
          light small absolute right middle fab>
          <v-icon>add</v-icon>
        </v-btn>
        <div slot="content">
          <v-card-title>
            <v-select
              v-model="searchCreatedBy"
              label="Created by"
              :items="['ALL', 'SYS', 'USER']"
              single-line
              hide-details
            ></v-select>
            <v-spacer></v-spacer>
            <v-spacer></v-spacer>
            <v-text-field
              v-model="searchName"
              label="Name"
              append-icon="search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-card flat>
            <v-data-table
              :headers="headers"
              :rows-per-page-items=[10,25,50,100]
              :items="filteredConcepts"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <tr @click="navigateTo({name: 'concept', params: { conceptid: props.item.conceptid }})" class="concept-link">
                  <td class="text-xs-left">{{ props.item.conceptid }}</td>
                  <td class="text-xs-left">{{ props.item.concept }}</td>
                  <td class="text-xs-left">{{ props.item.linksto }}</td>
                  <td>{{ props.item.isnumeric}}</td>
                  <td class="text-xs-left">{{ props.item.created_by }}</td>
                </tr>
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
      ],
      searchCreatedBy: '',
      searchName: ''
    }
  },
  methods: {
    navigateTo (route) {
      console.log(route)
      this.$router.push(route)
    }
  },
  async mounted () {
    this.concepts = (await ConceptsService.index()).data
    console.log('Mounted Concepts', this.concepts)
  },
  computed: {
    filteredConcepts () {
      const { searchCreatedBy, searchName } = this
      console.log('filteredConcepts')

      return this.concepts
        .filter(concept => searchName === '' || concept.concept.toLowerCase().indexOf(searchName.toLowerCase()) > -1)
        .filter(concept => searchCreatedBy === 'ALL' || searchCreatedBy === '' || concept.created_by === searchCreatedBy)
    }
  }
}
</script>

<style scoped>
  tr.concept-link td {
    cursor: pointer;
  }

  tr.concept-link:hover td {
    color: blue;
  }
</style>
