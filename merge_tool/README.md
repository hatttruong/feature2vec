# Merge tool #

## Setup

[Link](https://www.youtube.com/watch?v=Fa4cRMaTDUI&list=PLWKjhJtqVAbnadueQ-C5keMQQiQau_i0D)

### Install

```
# Install NodeJs

# Install Vue-Cli
$ npm install -g vue-cli
```

### CLIENT SETUP

```
$ vue init webpack client
? Project name client
? Project description a Vue.js project
? Author Ha Truong <thuha0921@gmail.com>
? Vue build standalone
? Install vue-router? Yes
? Use ESLint to lint your code? Yes
? Pick an ESLint preset Standard
? Set up unit tests Yes
? Pick a test runner karma
? Setup e2e tests with Nightwatch? Yes

$ cd client
$ npm run dev
```

### SERVER SETUP

* nodemon: restart the server every time we change something in our code
* express:
* body-parser: parse Json
* morgan: logger
* cors: 

```
$ cd ../
$ mkdir server
$ cd server
$ npm init -f
$ npm install --save nodemon eslint express body-parser cors morgan

```

Edit `package.json` with the following changes:

```javascript
"scripts": {
    "start": "./node_modules/nodemon/bin/nodemon.js src/app.js --exec 'npm run lint && node'",
    "lint": "./node_modules/.bin/eslint **/*.js"
  }
```

Install `eslint`:

```
$ node ./node_modules/eslint/bin/eslint.js  --init
? How would you like to configure ESLint? Use a popular style guide
? Which style guide do you want to follow? Standard (https://github.com/standard/standard)
? What format do you want your config file to be in? JavaScript

```

Start server: `npm start`

## Implement Request

```
# under Client folder, install axios for doing HTTP requests
$ npm install --save axios
```

## Connect Postgresql

We use`Sequelize` - a ORM interface to connect to Postgres

```
npm install -g sequelize-cli
npm install --save sequelize pg pg-hstore
```
* **pg** will be responsible for creating the database connection
* **pg-hstore** is a module for serializing and deserializing JSON data into the Postgres hstore format.



## Validating data

```
cd server
npm install --save joi
```

## Theme

```
cd client
npm install --save vuetify
```
## Login

* jsonwebtoken: generate token from json object
* bcrypt-nodejs: using to hash string
```
cd server
npm install --save jsonwebtoken
npm install --save bcrypt-nodejs
npm install --save bluebird
```
## Vuex


```
cd client
npm install --save vuex
npm install --save vuex-router-sync
```

## Sequelize notes:
- At server side, `sequelize` works as an `ORM`, generate tables into database. But it is IMPORTANT to rememnber that:
    + Name of MODEL must be identical with name of TABLE. If it does not, we cannot get model in `Controller`, for example:
    ```javascript
    [models/Item.js]
    module.exports = (sequelize, DataTypes) => {
      const JvnItem = sequelize.define('JvnItem', {
          ...
      })
      return JvnItem
    }
  
    [controllers/ItemsController.js]
    const { JvnItem } = require('../models')
    ```
    + Remember to return model object in `models/XXX.js`
    + Sequelize automatically add "s" at the end of name of table in Postgresql (???), for example, `JvnItem` model will be `JvnItems` table
    + Sequelize uses double quotes when creating the tables and in Postgres, the tables where created using double quotes which makes the names case sensitive ("Devices" is a different name then Devices)

## Client Notes:
- load image: [read here](https://webpack.js.org/guides/asset-management/#loading-images)
    + install `file-loader`
    
    ```javascript
    npm install --save-dev file-loader
    ```
    
    + add the following rule into `build/webpage.base.conf.js`:
    
    ```javascript
    module: {
        rules: [
        ....
        {
            test: /\.(png|svg|jpg|gif)$/,
            use: [
              'file-loader'
            ]
        }
        ...
      ]
    }
    ```
## Done
- Load Concepts from DB
- Load Items from DB
- Items page:
    - Show distributions when click on Item: [example](https://codepen.io/metamet/pen/rrBEZr) (copy images to **static** folder)
    - Filter Items by: name
- Concepts page:
    - Filter Concepts by: name, created by
 
## TODO
- Items page:
    - Show list of values when click on Item
- Concepts page:
    - Show items belong to Concepts
- Merge page:
    - show distributions
    - drag & drop categories values
    - save object to postgres