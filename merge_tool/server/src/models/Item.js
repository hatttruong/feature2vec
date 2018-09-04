module.exports = (sequelize, DataTypes) => {
  const Item = sequelize.define('jvn_item_mapping', {
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
    category_values: DataTypes.STRING(500),
    min: DataTypes.DOUBLE,
    percentile_25th: DataTypes.DOUBLE,
    percentile_50th: DataTypes.DOUBLE,
    percentile_75th: DataTypes.DOUBLE,
    max: DataTypes.DOUBLE,
    distribution_img: DataTypes.STRING(500)
  }, {
    classMethods: {
      associate: (models) => {
        console.log(models.jvn_concepts)
        Item.belongsTo(models.jvn_concepts, { foreignKey: 'candidate_concept_id', as: 'CandidateConcept' })
        Item.belongsTo(models.jvn_concepts, { foreignKey: 'concept_id', as: 'Concept' })
      }
    }
  })
  // Item.hasOne(Concept, { as: 'CandidateConcept', foreignKey: 'candidate_concept_id' })
  // Item.hasOne(Concept, { as: 'Concept', foreignKey: 'concept_id' })
  return Item
}
