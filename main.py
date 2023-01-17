from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRoundFlatIconButton, MDIconButton
from kivymd.uix.label import MDLabel
#from kivy.uix.button import Button

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivy.properties import StringProperty
from kivy.metrics import dp

from kivymd.uix.pickers import MDDatePicker
import datetime
import locale

from kivymd.uix.tab import MDTabsBase
#from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import GridLayout
#from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.datatables import MDDataTable

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import numpy as np

import cv2
from pyzbar import pyzbar

from kivy.uix.popup import Popup


import sqlite3

theme = "Light"
s = ""
start = ''
end  = ''
start1 = ''
end1  = ''
locale.setlocale(locale.LC_ALL, 'uk_UA')

kv = Builder.load_file("windows.kv")

def invalidInsert():
    pop = Popup(title='Помилка сканування чеку',
        content=MDLabel(text='Введіть дані вручну!'),
        size_hint=(None, None), size=(300, 200))
    pop.open()

class Item(OneLineIconListItem):
    text = StringProperty()

class WindowManager(ScreenManager):
    pass

class Tab(MDFloatLayout, MDTabsBase):
    pass

#Main Screen
class MainWindow(Screen):
    
    def category(self):
        self.manager.current = "category"

    def check(self):
        self.manager.current = "check"
        
    def table(self): 
        self.manager.current = "table"

    def income(self):
        self.manager.current = "income"

    def chart(self): 
        self.manager.current = "chart"

    def setting(self):
       self.manager.current = "setting"
        
    def scan(self):
        global data_video, price_video
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()   
        while True:
            ret, frame = camera.read()
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                x, y , w, h = barcode.rect
                #розшифровуємо інформацію зі QR-коду
                barcode_info = barcode.data.decode('utf-8')                
                cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)            
                try:
                    #розбиваємо розшифрований текст зі QR-коду на масив слів            
                    list = barcode_info.split(' ')
                    data_video = list[4]
                    price_video = list[2].strip('=')
                    self.manager.current = "checkvideo"                       
                except:
                    invalidInsert()                                 
                #додаємо текст поверх створеного прямокутника
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)
            #запускаємо камеру
            cv2.imshow('Video', frame)
            #виходимо з програми після першого сканування QR-коду
            if len(barcodes) > 0 & cv2.waitKey(1):
                camera.release()
                cv2.destroyAllWindows()
                break
            elif cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
                cv2.destroyAllWindows()
                break

#Chart Screen
class ChartWindow(Screen):
    def main(self): 
        self.manager.current = "main"

    def on_enter(self):
        today = datetime.datetime.now()
        self.ids.day1.text = datetime.datetime.strftime(today, '%d.%m.%Y')        
        self.chart1()    

    def show_chart_picker1(self):        
        date_dialog = MDDatePicker(
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            )
        date_dialog.bind(on_save=self.on_save1)
        date_dialog.open()

    def on_save1(self, instance, value, date_range):
        date = value.strftime("%d.%m.%Y")
        self.ids.day1.text = str(date)
        self.chart1()

    def show_chart_picker2(self):        
        date_dialog = MDDatePicker(
            mode="range",
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            )
        date_dialog.bind(on_save=self.on_save2)
        date_dialog.open()        
        
    def on_save2(self, instance, value, date_range):
        global start1
        global end1
        start1 = date_range[0].strftime("%d.%m.%Y")
        end1 = value.strftime("%d.%m.%Y")
        self.ids.day2.text = str(start1)+" - "+str(end1)
        self.chart2()

    def show_chart_picker3(self):        
        date_dialog = MDDatePicker(
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            
            )
        date_dialog.bind(on_save=self.on_save3)
        date_dialog.open()        
        
    def on_save3(self, instance, value, date_range):
        date = value.strftime("%Y")       
        self.ids.day3.text = str(date)
        self.chart3()
        
    def chart1(self):
        self.ids.chart1.clear_widgets()
        plt.clf()
        x = []
        names = []
        
        text = self.ids.day1.text        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT price FROM category, costs Where costs.category=id_category and data='"+str(text)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            x += rows            
            rows = cursor.fetchone()

        sql1 = "SELECT name FROM category, costs Where costs.category=id_category and data='"+str(text)+"'"
        cursor.execute(sql1)
        rows1 = cursor.fetchone()
        while rows1:            
            names += rows1
            rows1 = cursor.fetchone() 
       
        x = np.array(x)
        names = np.array(names)  
        rects = plt.bar(names, x, color='black')
        plt.xlabel('Категорії')
        plt.ylabel('Витрати')
        
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2., 1.0 * height, '%d' % int(height), ha='center', va='bottom',color='brown')
        
        self.ids.chart1.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def chart2(self):
        self.ids.chart2.clear_widgets()
        plt.clf()
        x = []
        names = []
        
        text1 = start1
        text2 = end1       
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT price FROM category, costs Where costs.category=id_category and data >= '"+str(text1)+"' AND data <= '"+str(text2)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            x += rows            
            rows = cursor.fetchone()

        sql = "SELECT name FROM category, costs Where costs.category=id_category and data >= '"+str(text1)+"' AND data <= '"+str(text2)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:            
            names += rows            
            rows = cursor.fetchone() 
       
        x = np.array(x)
        names = np.array(names)
        print(x)
        print(names)
        
        rects = plt.bar(names, x, color='brown')               
        plt.xlabel('Категорії')
        plt.ylabel('Витрати')
        
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2., 1.0 * height, '%d' % int(height), ha='center', va='bottom',color='brown')
        
        self.ids.chart2.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def chart3(self):
        self.ids.chart3.clear_widgets()
        plt.clf()
        x = []
        names = []
        
        text = self.ids.day3.text        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT price FROM category, costs Where costs.category=id_category and substr(data,7,5)='"+str(text)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            x += rows            
            rows = cursor.fetchone()

        sql1 = "SELECT name FROM category, costs Where costs.category=id_category and substr(data,7,5)='"+str(text)+"'"
        cursor.execute(sql1)
        rows1 = cursor.fetchone()
        while rows1:            
            names += rows1           
            rows1 = cursor.fetchone() 
       
        x = np.array(x)
        names = np.array(names)
               
        rects = plt.bar(names, x, color='brown')               
        plt.xlabel('Категорії')
        plt.ylabel('Витрати')
        
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2., 1.0 * height, '%d' % int(height), ha='center', va='bottom',color='brown')
        
        self.ids.chart3.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        
    def on_chart_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):        
        today = datetime.datetime.now()
        if instance_tab.name == 'tab1_chart':             
            self.ids.day1.text = datetime.datetime.strftime(today, '%d.%m.%Y')
            self.chart1()

        if instance_tab.name == 'tab2_chart':             
            self.ids.day2.text = datetime.datetime.strftime(today, '%d.%m.%Y')
            self.chart2()

        if instance_tab.name == 'tab3_chart':             
            self.ids.day3.text = datetime.datetime.strftime(today, '%Y')
            self.chart3()


#Table Screen
class TableWindow(Screen):
    def main(self): 
        self.manager.current = "main"

    def on_enter(self):
        today = datetime.datetime.now()
        self.ids.day1_label.text = datetime.datetime.strftime(today, '%d.%m.%Y')        
        self.show_date()    

    def show_date_picker1(self):        
        date_dialog = MDDatePicker(
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            )
        date_dialog.bind(on_save=self.on_save1)
        date_dialog.open()

    def on_save1(self, instance, value, date_range):
        date = value.strftime("%d.%m.%Y")
        self.ids.day1_label.text = str(date)
        self.show_date()       
    

    def show_date_picker2(self):        
        date_dialog = MDDatePicker(
            mode="range",
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            )
        date_dialog.bind(on_save=self.on_save2)
        date_dialog.open()        
        
    def on_save2(self, instance, value, date_range):
        global start
        global end
        start = date_range[0].strftime("%d.%m.%Y")
        end = value.strftime("%d.%m.%Y")
        self.ids.day2_label.text = str(start)+" - "+str(end)
        self.show_period()

    def show_date_picker3(self):        
        date_dialog = MDDatePicker(
            primary_color="darkorange",
            accent_color="black",
            text_color="white",
            text_button_color="white",
            selector_color="brown",
            
            )
        date_dialog.bind(on_save=self.on_save3)
        date_dialog.open()        
        
    def on_save3(self, instance, value, date_range):
        date = value.strftime("%Y")       
        self.ids.day3_label.text = str(date)
        self.show_year()
        
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):        
        today = datetime.datetime.now()
        if instance_tab.name == 'tab1':             
            self.ids.day1_label.text = datetime.datetime.strftime(today, '%d.%m.%Y')
            self.show_date()
            
        if instance_tab.name == 'tab2':            
            self.ids.day2_label.text = datetime.datetime.strftime(today, '%d.%m.%Y')
            self.show_period()
            
        if instance_tab.name == 'tab3':           
            self.ids.day3_label.text = datetime.datetime.strftime(today, '%Y')            
            self.show_year()
  
    def show_date(self):
        self.ids.grid_tab1.clear_widgets()
        row = []
        text = self.ids.day1_label.text        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT data,price,name FROM category, costs Where costs.category=id_category and data='"+str(text)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            row += rows
            rows = cursor.fetchone()
        rowInfo = [(row)]
        colHeaders = [
            ("[color=#4a4939]Дата[/color]", dp(40)),
            ("[color=#4a4939]Витрати[/color]", dp(40)),
            ("[color=#4a4939]Категорія[/color]", dp(40))]
        table = MDDataTable(column_data=colHeaders,
                            size_hint=(1, 0.9),                            
                            background_color_header="#e7e4c0",                                                    
                            background_color_cell="#e7e4c0",
                            background_color_selected_cell="e7e4c0",
                            row_data=rowInfo)        
        self.ids.grid_tab1.add_widget(table)    

    def show_period(self):
        self.ids.grid_tab2.clear_widgets()
        row = []
        text1 = start
        text2 = end
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT data,price,name FROM category, costs Where costs.category=id_category and data >= '"+str(text1)+"' AND data <= '"+str(text2)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            row += rows
            rows = cursor.fetchone()
        rowInfo = [(row)]
        colHeaders = [
            ("[color=#4a4939]Дата[/color]", dp(40)),
            ("[color=#4a4939]Витрати[/color]", dp(40)),
            ("[color=#4a4939]Категорія[/color]", dp(40))]
        table = MDDataTable(column_data=colHeaders,
                            size_hint=(1, 0.9),                            
                            background_color_header="#e7e4c0",                                                    
                            background_color_cell="#e7e4c0",
                            background_color_selected_cell="e7e4c0",
                            row_data=rowInfo)        
        self.ids.grid_tab2.add_widget(table)

    def show_year(self):
        self.ids.grid_tab3.clear_widgets()
        row = []
        text = self.ids.day3_label.text        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        sql = "SELECT data,price,name FROM category, costs Where costs.category=id_category and substr(data,7,5)='"+str(text)+"'"
        cursor.execute(sql)
        rows = cursor.fetchone()
        while rows:
            row += rows
            rows = cursor.fetchone()
        rowInfo = [(row)]
        colHeaders = [
            ("[color=#4a4939]Дата[/color]", dp(40)),
            ("[color=#4a4939]Витрати[/color]", dp(40)),
            ("[color=#4a4939]Категорія[/color]", dp(40))]
        table = MDDataTable(column_data=colHeaders,
                            size_hint=(1, 0.9),                            
                            background_color_header="#e7e4c0",                                                    
                            background_color_cell="#e7e4c0",
                            background_color_selected_cell="e7e4c0",
                            row_data=rowInfo)        
        self.ids.grid_tab3.add_widget(table)
        
#CheckVideo Screen
class CheckVideoWindow(Screen):
    def main(self): 
        self.manager.current = "main"

    def on_enter(self):
        self.ids.drop_item.current_item = ""
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        tsql = "SELECT name FROM category"
        cursor.execute(tsql)
        rows = cursor.fetchall()        
        for row in rows:             
            menu_items = [
                {                                  
                    "text": str(row[0]),                    
                    "viewclass": "Item",
                    "height": dp(56),
                    "on_release": lambda x=str(row[0]): self.set_item(x),
                } for row in rows          
            ] 

        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,            
            width_mult=4,
        )            
        self.menu.bind()        
        
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.menu.dismiss()
        
    def addcheck(self):
        category = str(self.ids.drop_item.current_item)        
        if data_video != "" and price_video != "" and category != "":
            #зберігаємо в бд SQLite
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            query = "INSERT INTO costs(data, price, category) VALUES(?,?,?)"
            sql = cursor.execute("SELECT id_category FROM category WHERE name='"+category+"'").fetchone()[0]
            values = [data_video,price_video,sql]
            cursor.execute(query,values)
            db.commit()        
            self.manager.current = "main"
        else:
            invalidInsert()  

#Check Screen
class CheckWindow(Screen):
    def main(self): 
        self.manager.current = "main"

    def addcheck(self):
        data = self.ids.data.text
        price = self.ids.price.text
        category = str(self.ids.drop_item.current_item)
        if data != "" and price != "" and category != "":
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            query = "INSERT INTO costs(data, price, category) VALUES(?,?,?)"
            sql = cursor.execute("SELECT id_category FROM category WHERE name='"+category+"'").fetchone()[0]
            values = [data,price,sql]
            cursor.execute(query,values)
            db.commit()        
            self.manager.current = "main"
    
    def on_enter(self):
        self.ids.data.text = ""
        self.ids.price.text = ""
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        tsql = "SELECT name FROM category"
        cursor.execute(tsql)
        rows = cursor.fetchall()        
        for row in rows:             
            menu_items = [
                {                                  
                    "text": str(row[0]),                    
                    "viewclass": "Item",
                    "height": dp(56),
                    "on_release": lambda x=str(row[0]): self.set_item(x),
                } for row in rows          
            ] 

        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,            
            width_mult=4,
        )            
        self.menu.bind()
        self.ids.drop_item.text=s
        
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.menu.dismiss()


#Settings Screen

class SettingWindow(Screen):
    def main(self):
        self.manager.current = "main"



#DeleteCategory Screen
class DeleteCategoryWindow(Screen):
    def category(self):         
        self.manager.current = "category"

    def on_enter(self):
        self.ids.drop_item.current_item = ""
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        tsql = "SELECT name FROM category"
        cursor.execute(tsql)
        rows = cursor.fetchall()        
        for row in rows:             
            menu_items = [
                {                                  
                    "text": str(row[0]),                    
                    "viewclass": "Item",
                    "height": dp(56),
                    "on_release": lambda x=str(row[0]): self.set_item(x),
                } for row in rows          
            ] 

        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,            
            width_mult=4,
        )            
        self.menu.bind()        
        
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.menu.dismiss()

    def deletecategory(self):
        name = str(self.ids.drop_item.current_item)        
        if name != "":
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            query = "DELETE FROM category WHERE name='"+str(name)+"'"
            cursor.execute(query)
            db.commit()        
            self.manager.current = "category"

#AddCategory Screen
class AddCategoryWindow(Screen):
    def category(self):         
        self.manager.current = "category"

    def addcategory(self, MDIconButton):
        name = self.ids.name.text
        icon = str(MDIconButton.icon)               
        if name != "":
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            query = "INSERT INTO category(name, icon) VALUES('"+str(name)+"', '"+str(icon)+"')"
            cursor.execute(query)
            db.commit()        
            self.manager.current = "category"
            
    def on_enter(self):
        self.ids.grid.clear_widgets()
        data = ['bus', 'city', 'gift', 'phone', 'tennis', 'web', 'yoga', 'cart', 'heart', 'hiking', 'human', 'phone']
        for t in data:            
            self.ids.grid.add_widget(                
                MDIconButton(
                    id=str(t),
                    icon=t,                    
                    theme_icon_color="Custom",
                    pos_hint={"center_x":.5},                    
                    md_bg_color="#e9dff7",
                    line_color="#e7e4c0",
                    text_color="#211c29",
                    icon_color="#6e6604",
                    width=120,
                    on_release= self.addcategory
                )
            )            
                
#Category Screen
class CategoryWindow(Screen):
    def main(self):         
        self.manager.current = "main"
        
    def addcategory(self):         
        self.manager.current = "addcategory"

    def deletecategory(self):         
        self.manager.current = "deletecategory"
        
    def check(self, MDRoundFlatIconButton):
        global s
        s = str(MDRoundFlatIconButton.text)       
        self.manager.current = "check" 
            
    def on_enter(self):
        self.ids.grid.clear_widgets()
        d = ["Додати категорію", "Видалити категорію"]
        for r in d:
            items_menu = [
                {
                    "text": r,
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "on_release": lambda x=r: self.menu_callback(x),
                } for r in d       
            ]
        self.menu = MDDropdownMenu(                
            items=items_menu,
            width_mult=4,
        )
        
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        tsql = "SELECT name, icon FROM category"
        cursor.execute(tsql)
        row = cursor.fetchone()        
        while row:
            name=str(row[0])
            self.ids.grid.add_widget(                
                MDRoundFlatIconButton(                    
                    icon=str(row[1]),
                    id=name,
                    text=str(row[0]),  
                    theme_icon_color="Custom",
                    pos_hint={"center_x":.5},                    
                    md_bg_color="#e9dff7",
                    line_color="#e7e4c0",
                    text_color="#211c29",
                    icon_color="#6e6604",
                    width=120,
                    on_release=self.check,                    
                )
            )            
            row = cursor.fetchone()
        
    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        if text_item == "Додати категорію":
            self.addcategory()
        if text_item == "Видалити категорію":
            self.deletecategory()
        self.menu.dismiss()
#---------------------------------------------------------------------------------------------
#Income Screen
class IncomeWindow(Screen):
    def main(self):
        self.manager.current = "main"



class CostAccounting(MDApp):
    def build(self):
        self.theme_cls.theme_style = theme
        return WindowManager()

    def close_app(self, *args):
        MDApp.get_running_app().stop()
        self.root_window.close()       

    def check(self, checkbox, value):
        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"



CostAccounting().run()
