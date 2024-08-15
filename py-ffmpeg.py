import os.
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QLineEdit, QComboBox, QProgressBar,
                             QMessageBox, QTabWidget, QInputDialog, QDialog)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QProcess, Qt, QTranslator, QLibraryInfo, QLocale, QUrl
from PyQt5.QtGui import QDesktopServices

class FFmpegGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.setWindowIcon(QIcon('ikonica.png'))
        self.process = None
        self.duration = 0
        self.input_file = ''
        self.output_file = ''
        self.formats = {
            'Video': ['mp4', 'avi', 'mkv', 'mov', 'flv', 'webm', 'wmv', 'mpeg', 'm4v', '3gp', 'vob', 'ts', 'mts', 'divx', 'asf'],
            'Audio': ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma', 'ac3', 'aiff', 'au', 'amr', 'ape', 'opus'],
            'Image': ['jpg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            'Other': ['swf', 'raw']
        }
        self.language_file = 'settings.txt'
        self.theme_file = 'theme.txt'
        self.initUI()
        self.loadLanguageSetting()
        self.loadThemeSetting()

    def initUI(self):
        self.setWindowTitle(self.tr('PyFFmpeg | English'))
        self.resize(500, 300)

        layout = QVBoxLayout()

        # Input file selection
        input_layout = QVBoxLayout()
        self.input_label = QLabel(self.tr('Select a file:'), self)
        input_sub_layout = QHBoxLayout()
        self.input = QLineEdit(self)
        self.browse_input_button = QPushButton(self.tr('Browse'), self)
        self.browse_input_button.clicked.connect(self.showInputDialog)
        input_sub_layout.addWidget(self.input)
        input_sub_layout.addWidget(self.browse_input_button)
        input_layout.addWidget(self.input_label)
        input_layout.addLayout(input_sub_layout)
        layout.addLayout(input_layout)

        # Output file selection
        output_layout = QVBoxLayout()
        self.output_label = QLabel(self.tr('Save converted file as:'), self)
        output_sub_layout = QHBoxLayout()
        self.output = QLineEdit(self)
        self.browse_output_button = QPushButton(self.tr('Browse'), self)
        self.browse_output_button.clicked.connect(self.showOutputDialog)
        output_sub_layout.addWidget(self.output)
        output_sub_layout.addWidget(self.browse_output_button)
        output_layout.addWidget(self.output_label)
        output_layout.addLayout(output_sub_layout)
        layout.addLayout(output_layout)

        # Output format selection
        format_layout = QVBoxLayout()
        self.format_label = QLabel(self.tr('Select output format:'), self)
        self.format_tab_widget = QTabWidget(self)
        self.populateFormatTabs()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_tab_widget)
        layout.addLayout(format_layout)

        # Convert button
        self.convert_button = QPushButton(self.tr('Convert'), self)
        self.convert_button.setFixedSize(100, 30)  # Set a fixed size for the Convert button
        self.convert_button.clicked.connect(self.convertVideo)
        layout.addWidget(self.convert_button)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(self.tr('Ready'), self)
        layout.addWidget(self.status_label)

        # Language, Theme, and About buttons layout
        button_layout = QHBoxLayout()
        self.about_button = QPushButton(self.tr('About'), self)
        self.about_button.clicked.connect(self.showAboutDialog)
        self.about_button.setFixedHeight(30)  # Set height for the About button
        self.language_button = QPushButton(self.tr('Change Language'), self)
        self.language_button.clicked.connect(self.changeLanguage)
        self.language_button.setFixedHeight(30)  # Set height for the Change Language button
        self.theme_button = QPushButton(self.tr('Theme'), self)
        self.theme_button.clicked.connect(self.changeTheme)
        self.theme_button.setFixedHeight(30)  # Set height for the Change Theme button
        button_layout.addWidget(self.about_button)
        button_layout.addWidget(self.language_button)
        button_layout.addWidget(self.theme_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.show()

    def populateFormatTabs(self):
        tab_labels = {
            'Video': self.tr('Video'),
            'Audio': self.tr('Audio'),
            'Image': self.tr('Image'),
            'Other': self.tr('Other'),
        }
        for category, formats in self.formats.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            combobox = QComboBox(tab)
            for fmt in formats:
                combobox.addItem(fmt)
            combobox.currentIndexChanged.connect(self.updateOutputExtension)
            tab_layout.addWidget(combobox)
            tab.setLayout(tab_layout)
            self.format_tab_widget.addTab(tab, tab_labels[category])
        self.format_tab_widget.currentChanged.connect(self.updateOutputExtension)

    def showInputDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, self.tr('Open file'), os.path.expanduser('~'))
        if fname:
            self.input_file = fname
            self.input.setText(fname)
            self.updateOutputPath()

    def showOutputDialog(self):
        default_name = self.generateUniqueOutputName()
        default_ext = self.getCurrentFormat()
        default_path = os.path.join(os.path.dirname(self.input_file), f"{default_name}.{default_ext}")
        fname, _ = QFileDialog.getSaveFileName(self, self.tr('Save file'), default_path, f"*.{default_ext}")
        if fname:
            self.output_file = fname
            self.output.setText(fname)

    def getCurrentFormat(self):
        current_tab = self.format_tab_widget.currentWidget()
        combobox = current_tab.findChild(QComboBox)
        current_format = combobox.currentText()
        return current_format

    def updateOutputPath(self):
        if self.input_file:
            default_name = self.generateUniqueOutputName()
            default_ext = self.getCurrentFormat()
            self.output_file = os.path.join(os.path.dirname(self.input_file), f"{default_name}.{default_ext}")
            self.output.setText(self.output_file)

    def generateUniqueOutputName(self):
        input_name = os.path.splitext(os.path.basename(self.input_file))[0]
        output_dir = os.path.dirname(self.input_file)
        base_name = input_name + "_converted"
        counter = 1
        while os.path.exists(os.path.join(output_dir, f"{base_name}.{self.getCurrentFormat()}")):
            base_name = f"{input_name}_converted_{counter}"
            counter += 1
        return base_name

    def updateOutputExtension(self):
        self.updateOutputPath()

    def convertVideo(self):
        if not self.input_file:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Please select an input file.'))
            return

        if not self.output_file:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Please specify an output file.'))
            return

        if os.path.exists(self.output_file):
            reply = QMessageBox.question(self, self.tr('File exists'),
                                         self.tr('The output file already exists. Do you want to overwrite it?'),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.status_label.setText(self.tr('Converting...'))
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.process = QProcess(self)
        self.process.finished.connect(self.onConversionFinished)
        self.process.readyReadStandardError.connect(self.updateProgress)
        self.process.start("ffmpeg", ["-i", self.input_file, self.output_file])

    def updateProgress(self):
        data = self.process.readAllStandardError().data().decode()
        if "Duration: " in data:
            duration_str = data.split("Duration: ")[1].split(",")[0].strip()
            h, m, s = map(float, duration_str.split(":"))
            self.duration = int(h * 3600 + m * 60 + s)

        if "time=" in data and self.duration > 0:
            time_str = data.split("time=")[1].split(" ")[0].strip()

            # Check if time_str is not 'N/A' before proceeding
            if time_str != 'N/A':
                h, m, s = map(float, time_str.split(":"))
                current_time = int(h * 3600 + m * 60 + s)
                progress = int((current_time / self.duration) * 100)
                self.progress_bar.setValue(progress)

    def parseCurrentTime(self, line):
        import re
        match = re.search(r"time=(\d+):(\d+):([\d.]+)", line)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            return hours * 3600 + minutes * 60 + seconds
        return None

    def onConversionFinished(self):
        self.status_label.setText(self.tr('Conversion finished.'))
        self.convert_button.setEnabled(True)
        self.progress_bar.setValue(100)

    def showAboutDialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle(self.tr('About PyFFmpeg'))

        about_layout = QVBoxLayout()
        about_label = QLabel(self.tr(
            '<h1>PyFFmpeg</h1>'
            '<p>Version 0.0.0.5</p>'
            '<p>A simple FFmpeg GUI built with PyQt5.</p>'
            '<p>Made by Црнобог | Crnobog</p>'
        ))
        about_label.setAlignment(Qt.AlignCenter)

        image_label = QLabel(self)
        image_label.setPixmap(QPixmap("ikonica.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignCenter)

        github_link = QLabel(self)
        github_link.setText('')
        github_link.setOpenExternalLinks(True)
        github_link.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        github_button = QPushButton(self.tr('GitHub'))
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/crnobog69/py-ffmpeg/')))
        close_button = QPushButton(self.tr('Close'))
        close_button.clicked.connect(about_dialog.accept)
        button_layout.addWidget(github_button)
        button_layout.addWidget(close_button)

        about_layout.addWidget(image_label)
        about_layout.addWidget(about_label)
        about_layout.addWidget(github_link)
        about_layout.addLayout(button_layout)

        about_dialog.setLayout(about_layout)
        about_dialog.exec_()

    def saveLanguageSetting(self, language):
       with open(self.language_file, 'w') as file:
           file.write(language)

    def loadLanguageSetting(self):
       try:
           with open(self.language_file, 'r') as file:
               language = file.read().strip()
               self.switchTranslator(language)
       except FileNotFoundError:
           self.switchTranslator('en')

    def switchTranslator(self, language):
       if language == 'en':
           self.translator.load(QLibraryInfo.location(QLibraryInfo.TranslationsPath))
       elif language == 'ja':
           self.translator.load('translations/ja.qm')
       elif language == 'sr':
           self.translator.load('translations/sr.qm')
       elif language == 'ru':
           self.translator.load('translations/ru.qm')
       elif language == 'es':
           self.translator.load('translations/es.qm')
       elif language == 'fr':
           self.translator.load('translations/fr.qm')
       elif language == 'de':
           self.translator.load('translations/de.qm')
       elif language == 'it':
           self.translator.load('translations/it.qm')
       elif language == 'kz':
           self.translator.load('translations/kz.qm')
       QApplication.instance().installTranslator(self.translator)
       self.retranslateUi()

    def retranslateUi(self):
       self.setWindowTitle(self.tr('PyFFmpeg | English'))
       self.input_label.setText(self.tr('Select a file:'))
       self.browse_input_button.setText(self.tr('Browse'))
       self.output_label.setText(self.tr('Save converted file as:'))
       self.browse_output_button.setText(self.tr('Browse'))
       self.format_label.setText(self.tr('Select output format:'))
       self.convert_button.setText(self.tr('Convert'))
       self.status_label.setText(self.tr('Ready'))
       self.about_button.setText(self.tr('About'))
       self.language_button.setText(self.tr('Change Language'))
       self.theme_button.setText(self.tr('Change Theme'))

       # Update the format tab labels
       tab_labels = {
           'Video': self.tr('Video'),
           'Audio': self.tr('Audio'),
           'Image': self.tr('Image'),
           'Other': self.tr('Other'),
       }
       for index in range(self.format_tab_widget.count()):
           category = list(self.formats.keys())[index]
           self.format_tab_widget.setTabText(index, tab_labels[category])

    def changeLanguage(self):
       languages = ['Српски (SR)', '日本語 (JP)', 'English (EN)', 'Русский (RU)', 'Español (ES)', 'Français (FR)', 'Deutsch (DE)', 'Italiano (IT)', 'Қазақша (KZ)']
       current_language = 'English (EN)'
       language, ok = QInputDialog.getItem(self, self.tr('Select Language'), self.tr('Language:'), languages, languages.index(current_language), False)
       if ok and language:
           if language == 'Српски (SR)':
               self.saveLanguageSetting('sr')
               self.switchTranslator('sr')
           elif language == '日本語 (JP)':
               self.saveLanguageSetting('ja')
               self.switchTranslator('ja')
           elif language == 'English (EN)':
               self.saveLanguageSetting('en')
               self.switchTranslator('en')
           elif language == 'Русский (RU)':
               self.saveLanguageSetting('ru')
               self.switchTranslator('ru')
           elif language == 'Español (ES)':
               self.saveLanguageSetting('es')
               self.switchTranslator('es')
           elif language == 'Français (FR)':
               self.saveLanguageSetting('fr')
               self.switchTranslator('fr')
           elif language == 'Deutsch (DE)':
               self.saveLanguageSetting('de')
               self.switchTranslator('de')
           elif language == 'Italiano (IT)':
               self.saveLanguageSetting('it')
               self.switchTranslator('it')
           elif language == 'Қазақша (KZ)':
               self.saveLanguageSetting('kz')
               self.switchTranslator('kz')

    def changeTheme(self):
        themes = ['Catppuccin Mocha Red', 'Rose Pine', 'Tokyo Night', 'Dracula', 'Nord', 'Gruvbox', 'Solarized', 'One Dark']
        current_theme = self.loadThemeSetting()
        theme, ok = QInputDialog.getItem(self, self.tr('---'), self.tr('Theme:'), themes, themes.index(current_theme), False)
        if ok and theme:
            self.applyTheme(theme)
            self.saveThemeSetting(theme)

    def applyTheme(self, theme):
        if theme == 'Catppuccin Mocha Red':
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1E2E;
                    color: #F5E0DC;
                }
                QPushButton {
                    background-color: #1E1E2E;
                    color: #F38BA8;
                    border: 1px solid #F38BA8;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #F38BA8;
                    color: #1E1E2E;
                }
                QLineEdit {
                    background-color: #1E1E2E;
                    color: #F5E0DC;
                    border: 1px solid #F38BA8;
                    padding: 5px;
                }
                QLabel {
                    color: #F38BA8;
                }
                QComboBox {
                    background-color: #181825;
                    color: #cdd6f4;
                    border: 1px solid #f38ba8;
                }
                QProgressBar {
                    background-color: #1E1E2E;
                    color: #F38BA8;
                    border: 1px solid #F38BA8;
                }
                QProgressBar::chunk {
                    background-color: #F38BA8;
                }
                QMessageBox {
                    background-color: #1E1E2E;
                    color: #F5E0DC;
                }
                QTabWidget::pane {
                    border: 1px solid #F38BA8;
                    background-color: #1E1E2E;
                }
                QTabWidget::tab-bar {
                    left: 5px;
                }
                QTabBar::tab {
                    background-color: #181825;
                    color: #F5E0DC;
                    border: 1px solid #F38BA8;
                    padding: 5px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected, QTabBar::tab:hover {
                    background-color: #F38BA8;
                    color: #1E1E2E;
                }
            """)
        elif theme == 'Rose Pine':
            self.setStyleSheet("""
                QWidget {
                    background-color: #191724; /* Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                }
                QPushButton {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #eb6f92; /* Rose Pine highlight */
                    color: #191724; /* Rose Pine background */
                }
                QLineEdit {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                    padding: 5px;
                }
                QLabel {
                    color: #e0def4; /* Rose Pine foreground */
                }
                QComboBox {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                }
                QProgressBar {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                }
                QProgressBar::chunk {
                    background-color: #9ccfd8; /* Rose Pine accent */
                }
                QMessageBox {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                }
                QTabWidget::pane {
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                }
                QTabWidget::tab-bar {
                    left: 5px;
                }
                QTabBar::tab {
                    background-color: #1f1d2e; /* Slightly lighter Rose Pine background */
                    color: #e0def4; /* Rose Pine foreground */
                    border: 1px solid #e0def4; /* Rose Pine foreground */
                    padding: 5px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected, QTabBar::tab:hover {
                    background-color: #eb6f92; /* Rose Pine highlight */
                    color: #191724; /* Rose Pine background */
                }
            """)
        elif theme == 'Tokyo Night':
            self.setStyleSheet("""
                QWidget {
                    background-color: #1A1B26;
                    color: #C0CAF5;
                }
                QPushButton {
                    background-color: #292E42;
                    color: #C0CAF5;
                    border: 1px solid #C0CAF5;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #C0CAF5;
                    color: #292E42;
                }
                QLineEdit {
                    background-color: #292E42;
                    color: #C0CAF5;
                    border: 1px solid #C0CAF5;
                    padding: 5px;
                }
                QLabel {
                    color: #C0CAF5;
                }
                QComboBox {
                    background-color: #292E42;
                    color: #C0CAF5;
                    border: 1px solid #C0CAF5;
                }
                QProgressBar {
                    background-color: #292E42;
                    color: #C0CAF5;
                    border: 1px solid #C0CAF5;
                }
                QProgressBar::chunk {
                    background-color: #C0CAF5;
                }
                QMessageBox {
                    background-color: #292E42;
                    color: #C0CAF5;
                }
                QTabWidget::pane {
                    border: 1px solid #C0CAF5;
                    background-color: #292E42;
                }
                QTabWidget::tab-bar {
                    left: 5px;
                }
                QTabBar::tab {
                    background-color: #292E42;
                    color: #C0CAF5;
                    border: 1px solid #C0CAF5;
                    padding: 5px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected, QTabBar::tab:hover {
                    background-color: #C0CAF5;
                    color: #292E42;
                }
            """)
        elif theme == 'Dracula':
            self.setStyleSheet("""
    QWidget {
        background-color: #282a36; /* Dracula background */
        color: #f8f8f2; /* Dracula foreground */
    }
    QPushButton {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
        border: 1px solid #f8f8f2; /* Dracula foreground */
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #f8f8f2; /* Dracula foreground */
        color: #282a36; /* Dracula background */
    }
    QLineEdit {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
        border: 1px solid #f8f8f2; /* Dracula foreground */
        padding: 5px;
    }
    QLabel {
        color: #f8f8f2; /* Dracula foreground */
    }
    QComboBox {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
        border: 1px solid #f8f8f2; /* Dracula foreground */
    }
    QProgressBar {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
        border: 1px solid #f8f8f2; /* Dracula foreground */
    }
    QProgressBar::chunk {
        background-color: #50fa7b; /* Dracula green */
    }
    QMessageBox {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
    }
    QTabWidget::pane {
        border: 1px solid #f8f8f2; /* Dracula foreground */
        background-color: #44475a; /* Dracula current line */
    }
    QTabWidget::tab-bar {
        left: 5px;
    }
    QTabBar::tab {
        background-color: #44475a; /* Dracula current line */
        color: #f8f8f2; /* Dracula foreground */
        border: 1px solid #f8f8f2; /* Dracula foreground */
        padding: 5px;
        margin-right: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #ff79c6; /* Dracula pink */
        color: #282a36; /* Dracula background */
    }
""")

        elif theme == 'Nord':
            self.setStyleSheet("""
    QWidget {
        background-color: #2E3440; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
    }
    QPushButton {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #88C0D0; /* Nord Frost */
        color: #2E3440; /* Nord Polar Night */
    }
    QLineEdit {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
        padding: 5px;
    }
    QLabel {
        color: #D8DEE9; /* Nord Snow Storm */
    }
    QComboBox {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
    }
    QProgressBar {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
    }
    QProgressBar::chunk {
        background-color: #A3BE8C; /* Nord Aurora Green */
    }
    QMessageBox {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
    }
    QTabWidget::pane {
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
        background-color: #3B4252; /* Nord Polar Night */
    }
    QTabWidget::tab-bar {
        left: 5px;
    }
    QTabBar::tab {
        background-color: #3B4252; /* Nord Polar Night */
        color: #D8DEE9; /* Nord Snow Storm */
        border: 1px solid #D8DEE9; /* Nord Snow Storm */
        padding: 5px;
        margin-right: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #88C0D0; /* Nord Frost */
        color: #2E3440; /* Nord Polar Night */
    }
""")
        elif theme == 'Gruvbox':
            self.setStyleSheet("""
    QWidget {
        background-color: #282828; /* Gruvbox background */
        color: #EBDBB2; /* Gruvbox foreground */
    }
    QPushButton {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #D79921; /* Gruvbox yellow */
        color: #282828; /* Gruvbox background */
    }
    QLineEdit {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
        padding: 5px;
    }
    QLabel {
        color: #EBDBB2; /* Gruvbox foreground */
    }
    QComboBox {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
    }
    QProgressBar {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
    }
    QProgressBar::chunk {
        background-color: #689D6A; /* Gruvbox aqua */
    }
    QMessageBox {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
    }
    QTabWidget::pane {
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
        background-color: #3C3836; /* Gruvbox slightly lighter background */
    }
    QTabWidget::tab-bar {
        left: 5px;
    }
    QTabBar::tab {
        background-color: #3C3836; /* Gruvbox slightly lighter background */
        color: #EBDBB2; /* Gruvbox foreground */
        border: 1px solid #EBDBB2; /* Gruvbox foreground */
        padding: 5px;
        margin-right: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #D79921; /* Gruvbox yellow */
        color: #282828; /* Gruvbox background */
    }
""")
        elif theme == 'Solarized':
            self.setStyleSheet("""
    QWidget {
        background-color: #002b36; /* Solarized background */
        color: #839496; /* Solarized foreground */
    }
    QPushButton {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
        border: 1px solid #839496; /* Solarized foreground */
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #268bd2; /* Solarized blue */
        color: #002b36; /* Solarized background */
    }
    QLineEdit {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
        border: 1px solid #839496; /* Solarized foreground */
        padding: 5px;
    }
    QLabel {
        color: #839496; /* Solarized foreground */
    }
    QComboBox {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
        border: 1px solid #839496; /* Solarized foreground */
    }
    QProgressBar {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
        border: 1px solid #839496; /* Solarized foreground */
    }
    QProgressBar::chunk {
        background-color: #859900; /* Solarized green */
    }
    QMessageBox {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
    }
    QTabWidget::pane {
        border: 1px solid #839496; /* Solarized foreground */
        background-color: #073642; /* Solarized slightly lighter background */
    }
    QTabWidget::tab-bar {
        left: 5px;
    }
    QTabBar::tab {
        background-color: #073642; /* Solarized slightly lighter background */
        color: #839496; /* Solarized foreground */
        border: 1px solid #839496; /* Solarized foreground */
        padding: 5px;
        margin-right: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #268bd2; /* Solarized blue */
        color: #002b36; /* Solarized background */
    }
""")
        elif theme == 'One Dark':
            self.setStyleSheet("""
    QWidget {
        background-color: #000000; /* Pure black */
        color: #ffffff; /* White for text */
    }
    QPushButton {
        background-color: #1c1c1c; /* Slightly lighter black for buttons */
        color: #ffffff; /* White text */
        border: 1px solid #333333; /* Dark gray border */
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #333333; /* Dark gray on hover */
        color: #ffffff; /* White text */
    }
    QLineEdit {
        background-color: #1c1c1c; /* Slightly lighter black */
        color: #ffffff; /* White text */
        border: 1px solid #333333; /* Dark gray border */
        padding: 5px;
    }
    QLabel {
        color: #ffffff; /* White text */
    }
    QComboBox {
        background-color: #1c1c1c; /* Slightly lighter black */
        color: #ffffff; /* White text */
        border: 1px solid #333333; /* Dark gray border */
    }
    QProgressBar {
        background-color: #1c1c1c; /* Slightly lighter black */
        color: #ffffff; /* White text */
        border: 1px solid #333333; /* Dark gray border */
    }
    QProgressBar::chunk {
        background-color: #4caf50; /* Green for progress chunk */
    }
    QMessageBox {
        background-color: #1c1c1c; /* Slightly lighter black */
        color: #ffffff; /* White text */
    }
    QTabWidget::pane {
        border: 1px solid #333333; /* Dark gray border */
        background-color: #1c1c1c; /* Slightly lighter black */
    }
    QTabWidget::tab-bar {
        left: 5px;
    }
    QTabBar::tab {
        background-color: #1c1c1c; /* Slightly lighter black */
        color: #ffffff; /* White text */
        border: 1px solid #333333; /* Dark gray border */
        padding: 5px;
        margin-right: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background-color: #333333; /* Dark gray */
        color: #ffffff; /* White text */
    }
""")

    def saveThemeSetting(self, theme):
        with open(self.theme_file, 'w') as f:
            f.write(theme)

    def loadThemeSetting(self):
        if os.path.exists(self.theme_file):
            with open(self.theme_file, 'r') as f:
                theme = f.read().strip()
            self.applyTheme(theme)
            return theme
        else:
            return 'Catppuccin Mocha Red'  # Default theme

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    locale = QLocale.system().name()
    qt_translator = QTranslator()
    qt_translator.load("qt_" + locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    gui = FFmpegGUI()
    gui.show()
    sys.exit(app.exec_())
