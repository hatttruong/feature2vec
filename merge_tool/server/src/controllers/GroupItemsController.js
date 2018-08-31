const { GroupItem } = require('../models')

module.exports = {
  async index (req, res) {
    try {
      const groupitems = await GroupItem.findAll({
        limit: 10
      })
      res.send(groupitems)
    } catch (e) {
      console.log('ERROR', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the group items'
      })
    }
  },
  async create (req, res) {
    try {
      const groupitem = await GroupItem.create(req.body)
      res.send(groupitem)
    } catch (err) {
      console.log('ERROR', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the group item'
      })
    }
  }
}
