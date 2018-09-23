// IMPORTANT: Name of Model must be identical with name of table
// Sequelize automatically add "s" at the end of name of table in Postgresql (???)
module.exports = (sequelize, DataTypes) => {
  const JvnItem = sequelize.define('JvnItem', {
    itemid: {
      type: DataTypes.INTEGER,
      unique: true,
      primaryKey: true
    },
    label: DataTypes.STRING(200),
    abbr: DataTypes.STRING(100),
    dbsource: DataTypes.STRING(20),
    linksto: DataTypes.STRING(50),
    isnumeric: DataTypes.BOOLEAN,
    unit: DataTypes.STRING(50),
    min_value: DataTypes.DOUBLE,
    percentile25th: DataTypes.DOUBLE,
    percentile50th: DataTypes.DOUBLE,
    percentile75th: DataTypes.DOUBLE,
    max_value: DataTypes.DOUBLE,
    distribution_img: DataTypes.STRING(500),
    conceptid: DataTypes.INTEGER
  })

  JvnItem.associate = function (models) {
    JvnItem.belongsToMany(models.JvnConcept, {
      foreignKey: 'itemid',
      through: 'JvnItemMapping',
      as: 'JvnConcept'
    })
  }

  return JvnItem
}
