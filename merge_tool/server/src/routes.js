const AuthenticationController = require('./controllers/AuthenticationController')
// const AuthenticationControllerPolicy = require('./policies/AuthenticationControllerPolicy')
const ItemsController = require('./controllers/ItemsController')
const ConceptsController = require('./controllers/ConceptsController')


module.exports = (app) => {
  app.post('/register',
    // AuthenticationControllerPolicy.register,
    AuthenticationController.register)
  app.post('/login',
    AuthenticationController.login)

  app.get('/items',
    ItemsController.index)
  app.get('/items/:itemid',
    ItemsController.show)
  app.post('/items',
    ItemsController.post)

  app.get('/concepts',
    ConceptsController.index)
  app.get('/concepts/:conceptid',
    ConceptsController.show)
  app.post('/create-concept',
    ConceptsController.post),
  app.put('/concepts/:conceptid',
    ConceptsController.put)
}