// IMPORTANT: Name of Model must be identical with name of table
module.exports = (sequelize, DataTypes) => {
  const JvnConcept = sequelize.define('JvnConcept', {
    conceptid: {
      type: DataTypes.INTEGER,
      unique: true,
      primaryKey: true
    },
    concept: DataTypes.STRING(200),
    isnumeric: DataTypes.BOOLEAN,
    linksto: DataTypes.STRING(50),
    created_by: DataTypes.STRING(100)
  })

  JvnConcept.associate = function (models) {
    JvnConcept.belongsToMany(models.JvnItem, {
      foreignKey: 'conceptid',
      through: 'JvnItemMapping',
      as: 'JvnConcept'
    })
  }

  return JvnConcept
}
