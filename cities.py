from cs50 import SQL
import csv

data = []

db = SQL("sqlite:///cities.db")

with open("worldcities.csv") as file:
    reader = csv.DictReader(file)
    
    for read in reader:
        data.append(read)
        
#names = db.execute("SELECT DISTINCT name FROM countries")
#name = []
#for x in names:
#    name.append(x["name"])

#for d in data:
#    country = db.execute("SELECT * FROM countries WHERE name = ?", d["country"])
#    country_id = country[0]["id"]
#    db.execute("INSERT INTO cities (id, name, country_id, latitude, longitude) VALUES (?, ?, ?, ?, ?)", d["id"], d["city"], country_id, d["lat"], d["lng"])
print(data[0]["city"])