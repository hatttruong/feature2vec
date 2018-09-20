const { JvnConcept } = require('../models')
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
  async create (req, res) {
    try {
      const concept = await JvnConcept.create(req.body)
      res.send(concept)
    } catch (err) {
      console.log('ERROR: func create: ', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the concept'
      })
    }
  }
}
