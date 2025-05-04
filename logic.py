import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates
     
    def get_country(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT country FROM cities WHERE city = ?", (city_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        
    def draw_city_region_map(self, path, city_name, padding_deg=10):
        coordinates = self.get_coordinates(city_name)
        if not coordinates:
            return False

        lat, lon = coordinates
        extent = [lon - padding_deg, lon + padding_deg, lat - padding_deg, lat + padding_deg]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.stock_img()
        ax.set_title(f"{city_name}")
        plt.plot(lon, lat, marker='o', color='red', transform=ccrs.Geodetic())
        plt.text(lon + 1, lat + 1, city_name, transform=ccrs.Geodetic())
        plt.savefig(path)
        plt.close()
        return True




    def create_grapf(self, path, cities, style):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()

        color = style['color']
        marker = style['marker']
        line_style = style['line_style']
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], color=color, marker=marker,
                    linestyle='None' if line_style == 'None' else line_style,
                    transform=ccrs.Geodetic())
                plt.text(lng + 3, lat + 12, city, horizontalalignment='left', transform=ccrs.Geodetic())

        plt.savefig(path)
        plt.close()
        
    def draw_distance(self, city1, city2):
        # Рисование линии между двумя городами для отображения расстояния
        city1_coords = self.get_coordinates(city1)
        city2_coords = self.get_coordinates(city2)
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.stock_img()
        plt.plot([city1_coords[1], city2_coords[1]], [city1_coords[0], city2_coords[0]], color='red', linewidth=2, marker='o', transform=ccrs.Geodetic())
        plt.text(city1_coords[1] + 3, city1_coords[0] + 12, city1, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.text(city2_coords[1] + 3, city2_coords[0] + 12, city2, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.savefig('distance_map.png')
        plt.close()


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()