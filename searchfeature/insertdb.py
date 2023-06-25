import sqlite3



x=""
conversation = ["M i think king is a big thing ","W i love queens"]# conversation i want to insert to DB

for i in conversation:
    x+=i+","


id = 1





con = sqlite3.connect('new_database.db')
cur = con.cursor()
# cur.execute("create table conversations(ID,text)")


# cur.execute(f"insert into conversations values('{id}','{x}')") #insert conversation into database

con.commit()    