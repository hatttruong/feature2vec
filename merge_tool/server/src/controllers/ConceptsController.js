const { JvnConcept, JvnItem } = require('../models')
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
      console.log('post concept:', req.body)

      // const concept = await JvnConcept.create(req.body)
      res.send(true)
    } catch (err) {
      console.log('ERROR: func post: ', err)
      res.status(500).send({
        error: 'an error has occurred trying to create the concept'
      })
    }
  }
}
