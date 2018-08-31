<template>
  <v-layout row>
    <v-flex xs4>
      <panel title="Group Info">
        <img v-if="this.loading" src="https://i.imgur.com/JfPpwOA.gif" />
        <div slot="content">
          <v-text-field
            label="Group Name"
            required
            :rules="[required]"
            v-model="group.group_name" >
          </v-text-field>
          <v-subheader>List Items</v-subheader>
          <v-list two-line>
            <template v-for="item in items">
              <v-list-tile
                :key="item.item_id">
                <v-list-tile-action>
                  <v-checkbox v-model="group.item_ids" v-bind:value="item.item_id"></v-checkbox>
                </v-list-tile-action>
                <v-list-tile-content>
                  <v-list-tile-title v-html="item.item_id"></v-list-tile-title>
                  <v-list-tile-sub-title v-html="item.label"></v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile>
            </template>
          </v-list>
        </div>
      </panel>
      <div class="danger-alert" v-if="error">
        {{error}}
      </div>
      <v-btn class="blue" dark @click="create">Create Group</v-btn>

    </v-flex>

    <!--Detail information-->
    <v-flex xs8>
      <v-tabs
        color="blue"
        dark
        class="ml-2"
        slider-color="yellow">
        <v-tab
          v-for="tab in this.tabs"
          :key="tab.id"
          ripple>
          {{ tab.name }}
        </v-tab>

        <v-tab-item v-for="tab in this.tabs"
          :key="tab.id">
          <!--General tab-->
          <v-card flat v-if="tab.id == 'general'">
            <v-data-table
              :headers="headers"
              :items="items"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.item_id }}</td>
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-left">{{ props.item.dbsource }}</td>
                <td>{{ props.item.isNumeric}}</td>
                <td>{{ props.item.min }}</td>
                <td>{{ props.item.percentile_25th }}</td>
                <td>{{ props.item.percentile_50th }}</td>
                <td>{{ props.item.percentile_75th }}</td>
                <td>{{ props.item.max }}</td>
              </template>
            </v-data-table>
          </v-card>

          <!--Distribution tab-->
          <v-card flat v-if="tab.id == 'distributions'">
            <v-container
              fluid
              grid-list-lg>
              <v-layout justify-space-around>
                <v-flex xs8>
                  <v-layout column>
                    <div v-for="item in items" :key="item.item_id">
                      <v-img src="https://picsum.photos/510/300?random" aspect-ratio="1.7"></v-img>
                      <v-card-title class="title">{{item.item_id}} - {{item.label}}</v-card-title>
                      <v-divider></v-divider>
                    </div>
                  </v-layout>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card>

          <!--Category Values tab-->
          <v-card flat v-if="tab.id == 'categoryvalues'">
            <v-data-table
              :headers="category_headers"
              :items="items"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.item_id }}</td>
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-left">{{ props.item.dbsource }}</td>
                <td class="text-xs-left">{{ props.item.values}}</td>
              </template>
            </v-data-table>
          </v-card>

        </v-tab-item>
      </v-tabs>
    </v-flex>
  </v-layout>
</template>

<script>
import Panel from '@/components/Panel'
import GroupItemsService from '@/services/GroupItemsService'

export default {
  name: 'MergeItems',
  components: {
    Panel
  },
  data () {
    return {
      loading: false,
      group: {
        group_name: null,
        item_ids: []
      },
      error: null,
      required: (value) => !!value || 'Required.',
      tabs: [
        {name: 'General', id: 'general'},
        {name: 'Distributions', id: 'distributions'},
        {name: 'Category Values', id: 'categoryvalues'}
      ],
      headers: [
        { text: 'Id', value: 'item_id' },
        { text: 'Name', value: 'label' },
        { text: 'Source', value: 'dbsource' },
        { text: 'Numeric', value: 'isNumeric' },
        { text: 'Min', value: 'min' },
        { text: '25th', value: 'percentile_25th' },
        { text: '50th', value: 'percentile_50th' },
        { text: '75th', value: 'percentile_75th' },
        {text: 'Max', value: 'max'}
      ],
      category_headers: [
        { text: 'Id', value: 'item_id' },
        { text: 'Name', value: 'label' },
        { text: 'Source', value: 'dbsource' },
        { text: 'Value', value: 'value' }
      ],
      items: [
        {
          dbsource: 'CareVue',
          item_id: 220,
          label: 'Heart Rate',
          isNumeric: true,
          min: 50,
          percentile_25th: 55,
          percentile_50th: 70,
          percentile_75th: 90,
          max: 100,
          values: ['abc', 'defg', '454656'],
          distributionImg: 'https://cdn.vuetifyjs.com/images/lists/1.jpg'
        },
        {
          dbsource: 'CareVue',
          item_id: 222,
          label: 'Heart rate',
          isNumeric: true,
          min: 50,
          percentile_25th: 56,
          percentile_50th: 80,
          percentile_75th: 99,
          max: 100,
          values: ['abc', 'defg', '454656'],
          distributionImg: 'https://cdn.vuetifyjs.com/images/lists/2.jpg'
        },
        {
          dbsource: 'Metavision',
          item_id: 220000,
          label: 'Heart Rate',
          isNumeric: true,
          min: 50,
          percentile_25th: 56,
          percentile_50th: 80,
          percentile_75th: 99,
          max: 100,
          values: ['abc', 'defg', '454656'],
          distributionImg: 'https://cdn.vuetifyjs.com/images/lists/3.jpg'
        },
        {
          dbsource: 'Metavision',
          item_id: 222000,
          label: 'Heart rate',
          isNumeric: true,
          min: 50,
          percentile_25th: 56,
          percentile_50th: 80,
          percentile_75th: 99,
          max: 100,
          values: ['abc', 'defg', '454656'],
          distributionImg: 'https://cdn.vuetifyjs.com/images/lists/4.jpg'
        }
      ]
    }
  },
  methods: {
    async create () {
      try {
        console.log(this.group)
        await GroupItemsService.create(this.group)
        this.$router.push({
          name: 'merge'
        })
      } catch (e) {
        console.log('error', e)
      }
    }
  }
}
</script>

<style scoped>

</style>
