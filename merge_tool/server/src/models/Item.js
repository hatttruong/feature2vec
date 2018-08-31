module.exports = (sequelize, DataTypes) => {
  const Item = sequelize.define('Item', {
    item_id: {
      type: DataTypes.INTEGER,
      unique: true,
      primaryKey: true
    },
    label: DataTypes.STRING,
    dbsource: DataTypes.STRING,
    linksto: DataTypes.STRING,
    isNumeric: DataTypes.BOOLEAN,
    unit: DataTypes.STRING,
    values: DataTypes.STRING,
    min: DataTypes.STRING,
    percentile_25th: DataTypes.STRING,
    percentile_50th: DataTypes.STRING,
    percentile_75th: DataTypes.STRING,
    max: DataTypes.STRING,
    distImage: DataTypes.STRING
  })

  return Item
}
