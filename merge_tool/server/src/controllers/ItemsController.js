const { JvnItem, JvnValueMapping } = require('../models')
console.log('JvnItem:', JvnItem)

module.exports = {
  async index (req, res) {
    try {
      console.log('Item:', JvnItem)
      let items = await JvnItem.findAll()
      res.send(items)
    } catch (e) {
      console.log('ERROR', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the items'
      })
    }
  },
  async show (req, res) {
    try {
      const item = await JvnItem.findById(req.params.itemid, {
        include: [{
          model: JvnValueMapping, as: 'JvnValueMapping' }]
      })
      res.send(item)
    } catch (e) {
      console.log('ERROR func findById', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the concepts'
      })
    }
  },
  async post (req, res) {
    try {
      const item = await JvnItem.create(req.body)
      res.send(item)
    } catch (err) {
      console.log('ERROR', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the item'
      })
    }
  }
}
