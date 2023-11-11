# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

from widgets import *
from modules import *
import cv2
import pandas
from tkinter import filedialog
from PIL import Image
import numpy as np
from turtle import width
import sys
import os
import platform
import datetime
import sqlite3
from functools import partial
from modules.conn_database import connect_database, create_table, close_database, delete_image

OPENSLIDE_PATH = "C:\\Users\\eyaam\\Code\\openslide-win64-20221217\\bin"
# import matplotlib.pyplot as plt

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
# FIX Problem for High DPI and Scale above 100%
os.environ["QT_FONT_DPI"] = "96"

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

processed_images = set()     

class MainWindow(QMainWindow):
        
    def __init__(self):
        # Connectez-vous à la base de données
        conn, cursor = connect_database("database.db")
        self.data_loaded = False
        # Créez la table si elle n'existe pas
        create_table(cursor)

        # Validez les modifications et fermez la connexion
        conn.commit()
        close_database(conn)
        print("Données de test ajoutées avec succès.")


        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "ESEO Dijon - Option E-Sante"
        description = "Cancer Detection APP"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(
            lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)

        # IMAGE_TREATEMENT WIDGETS
        widgets.pushButton.clicked.connect(self.buttonClick)
        # widgets.lineEdit.textChanged.connect(self.onTextChanged)
        # EXTRA LEFT BOX

        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(
            UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            self.load_data_to_table()
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(
                widgets.new_page)  # SET PAGE
            # RESET ANOTHERS BUTTONS SELECTED
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(
                btn.styleSheet()))  # SELECT MENU

        # if btnName == "btn_save":
        #     print("Save BTN clicked!")

        if btnName == "pushButton":
            
            img_path = filedialog.askopenfilename()
            saving_path = filedialog.askdirectory(
                title="Sélection du dossier de sauvegarde")
            widgets.lineEdit.setText("img_path")
            print(img_path)
            process_image(img_path, saving_path)

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')
        
        
         # Appel de la fonction pour charger les données
         

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////

    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # Add the process_image function here
    # Add the process_image function here
    def load_data_to_table(self):
        if not self.data_loaded:
            # Connexion à la base de données
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            # Exécutez votre requête SQL pour extraire les données
            cursor.execute("SELECT image_name, date_processed FROM images")

            # Récupérez toutes les lignes de résultats
            rows = cursor.fetchall()
            self.ui.tableWidget.insertColumn(4) 
            # Parcourez les lignes de résultats et remplissez le tableau
            for row_number, row_data in enumerate(rows, start=1):
                # Vérifiez si la ligne existe déjà
                if row_number < self.ui.tableWidget.rowCount():
                    # La ligne existe déjà, mettez simplement à jour les cellules
                    for column_number, column_data in enumerate(row_data):
                        if column_number == 0:
                            # Colonne "Image"
                            # Supprimez l'extension du nom de fichier
                            filename = os.path.splitext(column_data)[0]
                            item = QTableWidgetItem(filename)
                            self.ui.tableWidget.setItem(row_number, 0, item)
                        elif column_number == 1:
                            # Colonne "Date"
                            item = QTableWidgetItem(column_data)
                            self.ui.tableWidget.setItem(row_number, 1, item)

                    # Mettez à jour le nombre d'images dans les dossiers "Clean" et "Unusable"
                    image_name = os.path.splitext(row_data[0])[0]
                    clean_folder = f"C:\\Users\\eyaam\\Desktop\\ESEO\\projet\\notre projet\\git\\PFE_ESEO-master\\découpe\\{image_name}\\Clean"
                    unusable_folder = f"C:\\Users\\eyaam\\Desktop\\ESEO\\projet\\notre projet\\git\\PFE_ESEO-master\\découpe\\{image_name}\\Unusable"

                    num_clean_images = len([f for f in os.listdir(clean_folder) if os.path.isfile(os.path.join(clean_folder, f))])
                    num_unusable_images = len([f for f in os.listdir(unusable_folder) if os.path.isfile(os.path.join(unusable_folder, f))])

                    # Mettez à jour les colonnes "Cell" et "Line" du tableau
                    item = QTableWidgetItem(str(num_clean_images))
                    self.ui.tableWidget.setItem(row_number, 2, item)
                    item = QTableWidgetItem(str(num_unusable_images))
                    self.ui.tableWidget.setItem(row_number, 3, item)

                else:
                    # La ligne n'existe pas encore, insérez une nouvelle ligne
                    self.ui.tableWidget.insertRow(row_number)

                    for column_number, column_data in enumerate(row_data):
                        if column_number == 0:
                            # Colonne "Image"
                            # Supprimez l'extension du nom de fichier
                            filename = os.path.splitext(column_data)[0]
                            item = QTableWidgetItem(filename)
                            self.ui.tableWidget.setItem(row_number, 0, item)
                        elif column_number == 1:
                            # Colonne "Date"
                            item = QTableWidgetItem(column_data)
                            self.ui.tableWidget.setItem(row_number, 1, item)

                    # Mettez à jour le nombre d'images dans les dossiers "Clean" et "Unusable"
                    image_name = os.path.splitext(row_data[0])[0]
                    clean_folder = f"C:\\Users\\eyaam\\Desktop\\ESEO\\projet\\notre projet\\git\\PFE_ESEO-master\\découpe\\{image_name}\\Clean"
                    unusable_folder = f"C:\\Users\\eyaam\\Desktop\\ESEO\\projet\\notre projet\\git\\PFE_ESEO-master\\découpe\\{image_name}\\Unusable"

                    num_clean_images = len([f for f in os.listdir(clean_folder) if os.path.isfile(os.path.join(clean_folder, f))])
                    num_unusable_images = len([f for f in os.listdir(unusable_folder) if os.path.isfile(os.path.join(unusable_folder, f))])

                    # Mettez à jour les colonnes "Cell" et "Line" du tableau
                    item = QTableWidgetItem(str(num_clean_images))
                    self.ui.tableWidget.setItem(row_number, 2, item)
                    item = QTableWidgetItem(str(num_unusable_images))
                    self.ui.tableWidget.setItem(row_number, 3, item)

                # Ajout dynamique d'un bouton "Delete"
                btn = QPushButton("Delete")
                btn.clicked.connect(partial(self.delete_row, image_name))
                self.ui.tableWidget.setCellWidget(row_number, 4, btn)
            self.data_loaded = True

            # Close la connexion
            close_database(conn)
    def delete_row(self, image_name):
        # Supprimez la ligne ici
        current_row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(current_row)
        
        # Connexion à la base de données
        conn, cursor = connect_database("database.db")

        # Mettez à jour la base de données pour supprimer la ligne correspondante
        delete_image(cursor, image_name)

        # Validez les modifications et fermez la connexion
        conn.commit()
        close_database(conn)

def process_image(img_path, saving_path):
    if img_path not in processed_images:
        # The content of the process_image function
        OPENSLIDE_PATH = "C:\\Users\\eyaam\\Desktop\\ESEO\\projet\\notre projet\\git\\PFE_ESEO-master\\PFE_ESEO-master\\openslide-win64-20221217\\bin"
        
        if hasattr(os, 'add_dll_directory'):
            with os.add_dll_directory(OPENSLIDE_PATH):
                from openslide import OpenSlide
        else:
            from openslide import OpenSlide

        violet_threshold = 0.005
        black_threshold = 0.8
        white_threshold = 0.48

        img = OpenSlide(img_path)

        last_slash = img_path.rfind('/')
        point = img_path.rfind('_T')
        directory = img_path[last_slash + 1: point]

        dim = img.dimensions
        ratio = 2
        dim = (int(dim[0] / ratio), int(dim[1] / ratio))
        imageDL = img.get_thumbnail(dim)

        width, height = imageDL.size
        tileNumberHeight = 600
        tileNumberWidth = 600
        new_dir_path = saving_path + "/" + directory

        os.mkdir(new_dir_path)

        dir_ok = new_dir_path + "/Clean"
        dir_u = new_dir_path + "/Unusable"
        os.mkdir(dir_ok)
        os.mkdir(dir_u)

        for j in range(0, height, tileNumberHeight):
            top = j
            bottom = min(j + tileNumberHeight, height)

            for k in range(0, width, tileNumberWidth):
                left = k
                right = min(k + tileNumberWidth, width)
                box = (left, top, right, bottom)
                tile = imageDL.crop(box)
                largeur, hauteur = tile.size

                if largeur == 600 and hauteur == 600:
                    pixel_data = np.array(tile)
                    violet_mask = np.all(pixel_data >= [
                                        102, 0, 102], axis=-1) & np.all(pixel_data <= [255, 102, 255], axis=-1)
                    num_violet_pixels = np.sum(violet_mask)
                    total_pixels = pixel_data.shape[0] * pixel_data.shape[1]
                    percent_violet_pixels = 100 * num_violet_pixels / total_pixels

                    if percent_violet_pixels >= violet_threshold:
                        black_mask = pixel_data[:, :, 0] < 10
                        num_black_pixels = np.sum(black_mask)
                        percent_black_pixels = 100 * num_black_pixels / total_pixels
                        white_mask = pixel_data[:, :, 1] > 245
                        num_white_pixels = np.sum(white_mask)
                        percent_white_pixels = 100 * num_white_pixels / total_pixels

                        if percent_black_pixels <= black_threshold and percent_white_pixels <= white_threshold:
                            tile.save(f"{dir_ok}/{directory}{j}_{k}.png")
                        else:
                            tile.save(f"{dir_u}/{directory}{j}_{k}.png")
                    else:
                        tile.save(f"{dir_u}/{directory}_{j}_{k}.png")
                        
    
        print("fin de l'image " + directory)
        processed_images.add(img_path)
        #partie BDD d'image ajout
        conn, cursor = connect_database("database.db")
        cursor.execute("INSERT INTO images (image_name, date_processed) VALUES (?, ?)",
                    (directory, datetime.date.today()))  
        conn.commit()
        close_database(conn)
        print("image ajoutée à la BDD" )

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
    
