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
npm install --save joi
```



