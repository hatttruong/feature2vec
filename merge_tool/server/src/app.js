const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
const morgan = require('morgan')
const {sequelize} = require('./models')
const config = require('./config/config')

const app = express()
app.use(morgan('combined')) // log
app.use(bodyParser.json()) // parse json
app.use(cors())

require('./routes')(app)

// set force: true to force re-create database, if false, it only creates when does not exist
// sequelize.sync({force: true})
sequelize.sync({force: false})
  .then(() => {
    app.listen(config.port)

    console.log(`Server started on port ${config.port}`)
  })
