const { Sequelize } = require('sequelize');


const sequelize = new Sequelize('productdb', 'root', 'root', {
    host: process.env.DB_HOST,  
    dialect: 'mysql',           
});

module.exports = sequelize;
