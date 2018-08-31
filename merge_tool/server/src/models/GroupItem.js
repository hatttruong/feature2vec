module.exports = (sequelize, DataTypes) => {
  const GroupItem = sequelize.define('GroupItem', {
    id: {
      type: DataTypes.INTEGER,
      unique: true,
      primaryKey: true
    },
    name: DataTypes.STRING,
    createdBySystem: DataTypes.BOOLEAN
  })

  return GroupItem
}
