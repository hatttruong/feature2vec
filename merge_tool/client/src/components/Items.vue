<template>
  <v-layout row>
    <v-flex xs10 offset-xs1>
      <panel title="Items">
        <div slot="content">
          <v-card flat>
            <v-data-table
              :headers="headers"
              :rows-per-page-items=[10,25,50,100]
              :items="items"
              class="elevation-1">
              <template slot="items" slot-scope="props">
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
        { text: 'Id', value: 'itemid' },
        { text: 'Name', value: 'label' },
        { text: 'Source', value: 'dbsource' },
        { text: 'Linksto', value: 'linksto' },
        { text: 'Numeric', value: 'isnumeric' },
        { text: 'Min', value: 'min_value' },
        { text: '25th', value: 'percentile25th' },
        { text: '50th', value: 'percentile50th' },
        { text: '75th', value: 'percentile75th' },
        {text: 'Max', value: 'max_value'}
      ]
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
