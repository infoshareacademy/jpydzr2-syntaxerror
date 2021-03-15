import mysql
from mysql import connector

mydb = mysql.connector.connect(
  host="localhost",
  user="xxxxxx",
  password="xxxxxx"
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute('CREATE DATABASE IF NOT EXISTS Covid ')
mycursor.execute('USE Covid')



mycursor.execute('CREATE TABLE IF NOT EXISTS logs (id INT AUTO_INCREMENT, '
                 'date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, '
                 'log VARCHAR(100) NOT NULL,'
                 ' PRIMARY KEY (id))')
