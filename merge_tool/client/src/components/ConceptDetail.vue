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
            single-line
          </v-text-field>
          <v-checkbox
            label="Is numeric"
            :disabled="isViewMode"
            v-model="concept.isnumeric"
            single-line
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
          <v-card-title>
            <v-text-field
              v-model="searchName"
              append-icon="search"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-data-table
            :headers="selectedItemHeaders"
            :items="filteredItems"
            :hide-headers="true"
            v-model="selected"
            item-key="itemid"
            select-all
            class="elevation-1">
            <template slot="headerCell" slot-scope="props">
              <v-tooltip bottom>
                <span slot="activator">
                  {{ props.header.text }}
                </span>
                <span>
                  {{ props.header.text }}
                </span>
              </v-tooltip>
            </template>
            <template slot="items" slot-scope="props">
              <tr>
                <td>
                  <v-checkbox
                    v-model="props.selected"
                    primary
                    hide-details
                    @change="handleSelectedItem"
                  ></v-checkbox>
                </td>
                <td class="text-xs-left">{{ props.item.itemid }}</td>
                <td class="text-xs-left">{{ props.item.label }}</td>
              </tr>
            </template>
          </v-data-table>
        </div>
      </panel>
      <div class="danger-alert" v-if="error">
        {{error}}
      </div>
      <v-btn class="blue" dark @click="createOrEdit" v-if="!this.isViewMode">Done</v-btn>
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
              :headers="detailItemHeaders"
              :items="selected"
              :rows-per-page-items=[10,25,50,100]
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.itemid }}</td>
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-left">{{ props.item.dbsource }}</td>
                <td>{{ props.item.isnumeric}}</td>
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
                  <v-flex xs6 v-for="item in selected" :key="item.itemid">
                    <img v-bind:src="'/static/distributions/' + item.distribution_img" height="250px" />
                    <v-card-text class="title">{{item.itemid}} - {{item.label}}</v-card-text>
                  </v-flex>
                </v-layout>
              </v-container>
          </v-card>

          <!--Category Values tab-->
          <v-card flat v-if="tab.id == 'categoryvalues' && !concept.isnumeric">
            <v-data-table
              :headers="categoryHeaders"
              :items="selectedValueMapping"
              :rows-per-page-items=[25,50,100]
              class="elevation-1">
              <template slot="items" slot-scope="props">
                <td class="text-xs-left">{{ props.item.itemid }}</td>
                <td class="text-xs-left">{{ props.item.value }}</td>
                <td class="text-xs-left">{{ props.item.unified_value }}</td>
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
import ItemService from '@/services/ItemsService'

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
      selected: [],
      selectedItemHeaders: [
        { text: 'ItemId', value: 'itemid' },
        { text: 'Name', value: 'label' }
      ],
      searchCreatedBy: '',
      searchName: '',
      isViewMode: true,
      error: null,
      required: (value) => !!value || 'Required.',
      tabs: [
        {name: 'General', id: 'general'},
        {name: 'Distributions', id: 'distributions'},
        {name: 'Category Values', id: 'categoryvalues'}
      ],
      detailItemHeaders: [
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
      categoryHeaders: [
        { text: 'Id', value: 'itemid', sortable: !1 },
        { text: 'Value', value: 'value' },
        { text: 'Unified Value', value: 'unified_value' }
      ]
    }
  },
  async mounted () {
    // load all items which are not processed
    this.items = (await ItemService.index()).data
    for (const item of this.items) {
      item.JvnValueMapping = []
      item.JvnValueMapping.push({itemid: 1, value: 'abc', unified_value: 'abc 123'})
      item.JvnValueMapping.push({itemid: 2, value: 'def', unified_value: 'def 123'})
    }

    // load concept
    const conceptid = this.$route.params.conceptid
    if (conceptid > 0) {
      this.isViewMode = true
      this.concept = (await ConceptsService.show(conceptid)).data
      for (const selItem of this.concept.JvnItem) {
        selItem.JvnValueMapping = []
        selItem.JvnValueMapping.push({itemid: 1, value: 'abc', unified_value: 'abc 123'})
        selItem.JvnValueMapping.push({itemid: 2, value: 'def', unified_value: 'def 123'})
        this.selected.push(Object.assign({}, selItem))
      }
      console.log('this.selected', this.selected)
      console.log('this.concept', this.concept)
    } else {
      this.isViewMode = false
      this.concept = {name: '', isnumeric: false}
    }
  },
  computed: {
    filteredItems () {
      const { searchName, selected } = this
      return this.items
        .filter(item => selected.indexOf(item) > -1 || searchName === '' || item.label.toLowerCase().indexOf(searchName.toLowerCase()) > -1)
    },
    selectedValueMapping () {
      const valueMappings = []
      this.selected.forEach(item => valueMappings.push(item.JvnValueMapping))
      const flattened = [].concat(...valueMappings)
      console.log(flattened)
      return flattened
    }
  },
  methods: {
    async createOrEdit () {
      try {
        this.concept.JvnItem = this.selected
        console.log('createOrEdit', this.concept)

        if (this.concept.conceptid > 0) {
          await ConceptsService.put(this.concept)
        } else {
          await ConceptsService.post(this.concept)
        }
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
    handleSelectedItem () {
      console.log('handleIncludeItem: this.selected', this.selected)
    }
  }
}
</script>

<style scoped>

</style>
