const AuthenticationController = require('./controllers/AuthenticationController')
const AuthenticationControllerPolicy = require('./policies/AuthenticationControllerPolicy')
const ItemsController = require('./controllers/ItemsController')
const GroupItemsController = require('./controllers/GroupItemsController')


module.exports = (app) => {
  app.post('/register',
    // AuthenticationControllerPolicy.register,
    AuthenticationController.register)
  app.post('/login',
    AuthenticationController.login)

  app.get('/items',
    ItemsController.index)
  app.post('/items',
    ItemsController.post)

  app.get('/groupitems',
    GroupItemsController.index)
  app.post('/creategroup',
    GroupItemsController.create)
}