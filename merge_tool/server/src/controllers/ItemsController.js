const { JvnItem } = require('../models')
console.log('JvnItem:', JvnItem)

module.exports = {
  async index (req, res) {
    try {
      console.log('Item:', JvnItem)
      let items = await JvnItem.findAll()
      // {
      // limit: 10
      // }
      // )
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
