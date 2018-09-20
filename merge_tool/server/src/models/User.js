// TODO: encrypt password
// const Promise = require('bluebird')
// const bcrypt = Promise.promisifyAll(require('bcrypt-nodejs'))

// function hashPassword (user, options) {
//   const SALT_FACTOR = 8
//
//   if (!user.changed('password')) {
//     return
//   }
//
//   return bcrypt
//     .genSaltAsync(SALT_FACTOR)
//     .then(salt => bcrypt.hashAsync(user.password, salt))
//     .then(hash => {
//       user.setDataValue('password', hash)
//     })
// }
// IMPORTANT: Name of Model must be identical with name of table
module.exports = (sequelize, DataTypes) => {
  const JvnUser = sequelize.define('JvnUser', {
    email: {
      type: DataTypes.STRING,
      unique: true
    },
    password: DataTypes.STRING
  }
  // , {
  //   hooks: {
  //     beforeCreate: hashPassword,
  //     beforeUpdate: hashPassword,
  //     beforeSave: hashPassword
  //   }
  // }
  )

  JvnUser.prototype.comparePassword = function (password) {
    // return bcrypt.compareAsync(password, this.password)
    return password === this.password
  }

  JvnUser.associate = function (models) {
  }

  return JvnUser
}
