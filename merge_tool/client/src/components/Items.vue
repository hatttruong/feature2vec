<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Items">
        <div slot="content">
          <v-card flat>
            <v-card-title>
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="search"
                label="Search"
                single-line
                hide-details
              ></v-text-field>
            </v-card-title>
            <img v-if="this.loading" src="https://i.imgur.com/JfPpwOA.gif" />
            <v-data-table v-else
              :headers="headers"
              :rows-per-page-items=[10,25,50,100]
              :items="items"
              :search="search"
              item-key="itemid"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <tr @click="toggle(props.item.itemid)">
                  <td class="text-xs-left">{{ props.item.itemid }}</td>
                  <td class="text-xs-left">{{ props.item.label }}</td>
                  <td class="text-xs-left">{{ props.item.dbsource }}</td>
                  <td class="text-xs-left">{{ props.item.linksto }}</td>
                  <td>{{ props.item.isnumeric}}</td>
                  <td>{{ props.item.min_value }}</td>
                  <td>{{ props.item.percentile25th }}</td>
                  <td>{{ props.item.percentile50th }}</td>
                  <td>{{ props.item.percentile75th }}</td>
                  <td>{{ props.item.max_value }}</td>
                  <td>
                    <v-icon v-if="props.item.done">fas fa-check</v-icon>
                    <v-icon v-else>far fa-check</v-icon>
                  </td>
                </tr>
                <tr v-if="opened.includes(props.item.itemid)">
                  <td colspan="11" v-if="props.item.isnumeric">
                    <img v-bind:src="'/static/distributions/' + props.item.distribution_img" height="200px" />
                    <!--<v-img :src="'/static/distributions/' + props.item.distribution_img"></v-img>-->
                  </td>
                  <td colspan="10" v-else>
                    <v-data-table
                      :headers="categoryHeaders"
                      :items="props.item.JvnValueMapping"
                      :rows-per-page-items=[25,50,100]
                      class="elevation-1">
                      <template slot="items" slot-scope="props">
                          <td class="text-xs-left">{{ props.item.itemid }}</td>
                          <td class="text-xs-left">{{ props.item.value }}</td>
                          <td class="text-xs-left">{{props.item.unified_value}}</td>
                      </template>
                    </v-data-table>
                  </td>
                </tr>
              </template>
              <v-alert slot="no-results" :value="true" color="error" icon="warning">
                Your search for "{{ search }}" found no results.
              </v-alert>
            </v-data-table>
          </v-card>
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
      items: [],
      headers: [
        {text: 'Id', value: 'itemid'},
        {text: 'Name', value: 'label'},
        {text: 'Source', value: 'dbsource'},
        {text: 'Linksto', value: 'linksto'},
        {text: 'Numeric', value: 'isnumeric'},
        {text: 'Min', value: 'min_value'},
        {text: '25th', value: 'percentile25th'},
        {text: '50th', value: 'percentile50th'},
        {text: '75th', value: 'percentile75th'},
        {text: 'Max', value: 'max_value'},
        {text: 'Done', value: 'done'}
      ],
      categoryHeaders: [
        { text: 'Id', value: 'itemid', sortable: !1 },
        { text: 'Value', value: 'value', sortable: !1 },
        { text: 'Unified Value', value: 'unified_value', sortable: !1 }
      ],
      opened: [],
      search: '',
      loading: true
    }
  },
  async mounted () {
    this.items = (await ItemService.index()).data
    for (let item of this.items) {
      item.done = item.conceptid > 0
    }
    console.log('items', this.items)
    this.loading = false
  },
  methods: {
    async toggle (id) {
      console.log('load detail itemid=', id)
      const idxItem = this.items.findIndex(x => x.itemid === id)
      if (idxItem > -1 && !this.items[idxItem].JvnValueMapping) {
        const detailItem = (await ItemService.show(id)).data
        this.items[idxItem].JvnValueMapping = detailItem.JvnValueMapping
      }
      console.log('toggle id=', id)
      const index = this.opened.indexOf(id)
      console.log('opened?=', index > -1)

      if (index > -1) {
        this.opened.splice(index, 1)
      } else {
        this.opened.push(id)
      }
    }
  }
}
</script>

<style scoped>

</style>
