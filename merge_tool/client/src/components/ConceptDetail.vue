<template>
  <v-layout row>
    <v-flex xs4>
      <panel title="Concept Info">
        <img v-if="this.loading" src="https://i.imgur.com/JfPpwOA.gif" />
        <div slot="content">
          <v-text-field
            label="Concept Name"
            required
            :rules="[required]"
            :disabled="isViewMode"
            v-model="concept.concept" >
          </v-text-field>
          <v-checkbox
            label="Is numeric"
            :disabled="isViewMode"
            v-model="concept.isnumeric"
          ></v-checkbox>
          <!--<v-text-field-->
            <!--label="Created By"-->
            <!--required-->
            <!--:disabled=true-->
            <!--v-model="concept.created_by" >-->
          <!--</v-text-field>-->
          <!--<v-text-field-->
            <!--label="Created Date"-->
            <!--required-->
            <!--:disabled=true-->
            <!--v-model="concept.createdAt" >-->
          <!--</v-text-field>-->

          <v-subheader>LIST ITEMS</v-subheader>
          <v-list two-line>
            <template v-for="item in items">
              <v-list-tile
                :key="item.itemid">
                <v-list-tile-action>
                  <v-checkbox
                    v-model="checkedItems"
                    v-bind:value="item.itemid"
                    :disabled="isViewMode"
                    @change="handleIncludeItem"
                  ></v-checkbox>
                </v-list-tile-action>
                <v-list-tile-content>
                  <v-list-tile-title v-html="item.itemid"></v-list-tile-title>
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
      <v-btn class="blue" dark @click="createOrEdit" v-if="!this.isViewMode">Create</v-btn>
      <v-btn class="blue" dark @click="turnEditMode" v-if="!this.isViewMode">Cancel</v-btn>
      <v-btn class="blue" dark @click="turnEditMode" v-else>Edit</v-btn>
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
                <td class="text-xs-left">{{ props.item.itemid }}</td>
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-left">{{ props.item.dbsource }}</td>
                <td>{{ props.item.isNumeric}}</td>
                <td>{{ props.item.min_value }}</td>
                <td>{{ props.item.percentile25th }}</td>
                <td>{{ props.item.percentile50th }}</td>
                <td>{{ props.item.percentile75th }}</td>
                <td>{{ props.item.max_value }}</td>
              </template>
            </v-data-table>
          </v-card>

          <!--Distribution tab-->
          <v-card flat v-if="tab.id == 'distributions' && concept.isnumeric">
              <v-container fluid grid-list-lg text-xs-center>
                <v-layout row wrap>
                  <v-flex xs6 v-for="item in items" :key="item.itemid">
                    <img v-bind:src="'/static/distributions/' + item.distribution_img" height="250px" />
                    <v-card-text class="title">{{item.itemid}} - {{item.label}}</v-card-text>
                  </v-flex>
                </v-layout>
              </v-container>
          </v-card>

          <!--Category Values tab-->
          <v-card flat v-if="tab.id == 'categoryvalues' && !concept.isnumeric">
            <v-data-table
              :headers="category_headers"
              :items="items"
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.itemid }}</td>
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
import ConceptsService from '@/services/ConceptsService'

export default {
  name: 'ConceptDetail',
  components: {
    Panel
  },
  data () {
    return {
      loading: false,
      concept: [],
      items: [],
      checkedItems: [],
      isViewMode: true,
      error: null,
      required: (value) => !!value || 'Required.',
      tabs: [
        {name: 'General', id: 'general'},
        {name: 'Distributions', id: 'distributions'},
        {name: 'Category Values', id: 'categoryvalues'}
      ],
      headers: [
        { text: 'Id', value: 'itemid' },
        { text: 'Name', value: 'label' },
        { text: 'Source', value: 'dbsource' },
        { text: 'Numeric', value: 'isnumeric' },
        { text: 'Min', value: 'min_value' },
        { text: '25th', value: 'percentile25th' },
        { text: '50th', value: 'percentile50th' },
        { text: '75th', value: 'percentile75th' },
        {text: 'Max', value: 'max_value'}
      ],
      category_headers: [
        { text: 'Id', value: 'itemid' },
        { text: 'Name', value: 'label' },
        { text: 'Source', value: 'dbsource' },
        { text: 'Value', value: 'value' }
      ]
    }
  },
  async mounted () {
    const conceptid = this.$route.params.conceptid
    if (conceptid) {
      this.isViewMode = true
      this.concept = (await ConceptsService.show(conceptid)).data
      this.items = this.concept.JvnItem
      for (const item of this.items) {
        this.checkedItems.push(item.itemid)
      }
      console.log('Mounted Concept by id', this.concept)
    } else {
      // this.concept = (await ConceptsService.getSysConcepts(conceptid)).data
      console.log('TODO')
    }
  },
  methods: {
    async createOrEdit () {
      try {
        this.concept.updatedItemIds = this.checkedItems
        console.log('createOrEdit', this.concept)
        await ConceptsService.post(this.concept)
        this.$router.push({
          name: 'concepts'
        })
      } catch (e) {
        console.log('error[createOrEdit]', e)
      }
    },
    turnEditMode () {
      this.isViewMode = !this.isViewMode
    },
    handleIncludeItem (e) {
      // e.preventDefault()
      console.log('handleIncludeItem: this.checkedItems', this.checkedItems)
    }
  }
}
</script>

<style scoped>

</style>
