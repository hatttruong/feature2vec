const { User } = require('../models')
const jwt = require('jsonwebtoken')
const config = require('../config/config')

function jwtSignUser (user) {
  const ONE_WEEK = 60 * 60 * 7
  return jwt.sign(
    user,
    config.authentication.jwtSecret,
    {
      expiresIn: ONE_WEEK
    })
}

module.exports = {
  async register (req, res) {
    try {
      const user = await User.create(req.body)
      const userJson = user.toJSON()
      res.send({
        user: userJson,
        token: jwtSignUser(userJson)
      })
    } catch (err) {
      console.log(err)
      res.status(400).send({
        error: 'This user is already in use.'
      })
    }
  },
  async login (req, res) {
    try {
      const { email, password } = req.body
      console.log(email)
      console.log(password)
      const user = await User.findOne({
        where: {
          email: email
        }
      })
      console.log('user', user)

      if (!user) {
        res.status(403).send({
          error: 'The login information was incorrect'
        })
      } else {
        const isValidPassword = await user.comparePassword(password)
        console.log('isValidPassword', isValidPassword)

        if (!isValidPassword) {
          res.status(403).send({
            error: 'The login information was incorrect'
          })
        } else {
          const userJson = user.toJSON()
          res.send({
            user: userJson,
            token: jwtSignUser(userJson)
          })
        }
      }
    } catch (err) {
      console.log('ERROR', err)
      res.status(500).send({
        error: 'An error has occured trying to log in.'
      })
    }
  }
}
