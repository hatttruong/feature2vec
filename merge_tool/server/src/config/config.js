module.exports = {
  port: process.env.PORT || 8081,
  db: {
    database: process.env.DB_NAME || 'test',
    user: process.env.DB_USER || 'mimicuser',
    password: process.env.DB_PASS || '123456',
    options: {
      dialect: process.env.DIALECT || 'postgres',
      host: process.env.HOST || 'localhost'
    }
  }
}
