const { JvnConcept, JvnItem, JvnItemMapping, JvnValueMapping } = require('../models')
console.log('JvnConcept:', JvnConcept)

module.exports = {
  async index (req, res) {
    try {
      const concepts = await JvnConcept.findAll()
      res.send(concepts)
    } catch (e) {
      console.log('ERROR func index', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the concepts'
      })
    }
  },
  async search (req, res) {
    try {
      // const song = await Song.findById(req.params.songId)
      // res.send(song)
      const concepts = await JvnConcept.findAll()
      res.send(concepts)
    } catch (e) {
      console.log('ERROR func index', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the concepts'
      })
    }
  },
  async show (req, res) {
    try {
      console.log(JvnItem)
      const concept = await JvnConcept.findById(req.params.conceptid, { include: [{ model: JvnItem, as: 'JvnItem' }] })
      res.send(concept)
    } catch (e) {
      console.log('ERROR func findById', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the concepts'
      })
    }
  },
  async post (req, res) {
    try {
      const concept = req.body
      concept.created_by = 'USER'
      console.log('post concept:', concept)
      const result = await JvnConcept.create(concept)
      console.log('post concept result:', result)

      res.send(result)
    } catch (err) {
      console.log('ERROR: func post: ', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the concept'
      })
    }
  },
  async put (req, res) {
    try {
      const updatedConcept = req.body
      updatedConcept.created_by = 'USER'

      console.log('put concept:', updatedConcept)
      console.log('action=update')
      const result = await JvnConcept.update(updatedConcept, {
        where: {
          conceptid: req.params.conceptid
        }
      })

      const concept = await JvnConcept.findById(req.params.conceptid, { include: [{ model: JvnItem, as: 'JvnItem' }] })
      // delete concept.JvnItem which are not belong to updatedConcept.JvnItem
      for (const item of concept.JvnItem) {
        if (!updatedConcept.JvnItem.find(u => item.itemid === u.itemid)) {
          console.log('remove item:', item.itemid)
          JvnItemMapping.destroy({
            where: {
              conceptid: concept.conceptid,
              itemid: item.itemid
            }
          })

          await JvnItem.update({
            conceptid: -1
          }, {
            where: {
              itemid: item.itemid
            }
          })
        }
      }

      // insert updatedConcept.JvnItem which are not belong to concept.JvnItem
      for (const item of updatedConcept.JvnItem) {
        await JvnItem.update({
          conceptid: concept.conceptid
        }, {
          where: {
            itemid: item.itemid
          }
        })
        if (!concept.JvnItem.find(u => item.itemid === u.itemid)) {
          console.log('push item: ', item.itemid)
          await JvnItemMapping.create({
            conceptid: concept.conceptid,
            itemid: item.itemid
          })
        }
      }

      if (!updatedConcept.isnumeric && updatedConcept.JvnValueMapping) {
        // update JvnValueMapping
        for (const vm of updatedConcept.JvnValueMapping) {
          await JvnValueMapping.update({
            unified_value: vm.unified_value
          }, {
            where: {
              itemid: vm.itemid,
              value: vm.value
            }
          })
        }
      }

      if (result[0] === 1) {
        res.status(200).send({
          message: 'update successfully'
        })
      } else {
        res.send({
          error: 'error when updating'
        })
      }
    } catch (err) {
      console.log('ERROR: func post: ', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the concept'
      })
    }
  }
}
