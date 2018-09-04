const { Concept } = require('../models')

module.exports = {
  async index (req, res) {
    try {
      const concepts = await Concept.findAll({
        limit: 10
      })
      res.send(concepts)
    } catch (e) {
      console.log('ERROR func index', e)
      res.status(500).send({
        error: 'an error has occurred trying to fetch the concepts'
      })
    }
  },
  async create (req, res) {
    try {
      const concept = await Concept.create(req.body)
      res.send(concept)
    } catch (err) {
      console.log('ERROR: func create: ', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the concept'
      })
    }
  }
}
