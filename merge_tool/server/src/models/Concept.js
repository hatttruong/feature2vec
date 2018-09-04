module.exports = (sequelize, DataTypes) => {
  const Concept = sequelize.define('jvn_concepts', {
    conceptid: {
      type: DataTypes.INTEGER,
      unique: true,
      primaryKey: true
    },
    concept: DataTypes.STRING(200),
    created_by: DataTypes.STRING(100)
  })

  return Concept
}
