const { Item } = require('../models')

module.exports = {
  async index (req, res) {
    try {
      const items = await Item.findAll({
        limit: 10
      })
      res.send(items)
    } catch (e) {
      console.log('ERROR', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the items'
      })
    }
  },
  async post (req, res) {
    try {
      const item = await Item.create(req.body)
      res.send(item)
    } catch (err) {
      console.log('ERROR', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the item'
      })
    }
  }
}
