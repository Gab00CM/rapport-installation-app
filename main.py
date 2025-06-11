from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform

import os
import datetime
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import webbrowser
import urllib.parse
import subprocess
import platform

# Importations pour la génération PDF
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
except ImportError:
    print("ReportLab non installé. Installez avec: pip install reportlab")


class AccueilScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'accueil'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Titre
        titre = Label(
            text='Rapport d\'Installation',
            font_size='24sp',
            size_hint=(1, 0.2),
            color=(0.2, 0.6, 1, 1)
        )
        layout.add_widget(titre)
        
        # Boutons principaux
        btn_nouveau = Button(
            text='Nouveau Rapport',
            size_hint=(1, 0.15),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        btn_nouveau.bind(on_press=self.nouveau_rapport)
        
        btn_historique = Button(
            text='Historique',
            size_hint=(1, 0.15),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        btn_historique.bind(on_press=self.voir_historique)
        
        btn_config = Button(
            text='Configuration Email',
            size_hint=(1, 0.15),
            background_color=(0.7, 0.5, 0.2, 1)
        )
        btn_config.bind(on_press=self.config_email)
        
        layout.add_widget(btn_nouveau)
        layout.add_widget(btn_historique)
        layout.add_widget(btn_config)
        layout.add_widget(Label())  # Espace
        
        self.add_widget(layout)
    
    def nouveau_rapport(self, instance):
        self.manager.current = 'formulaire'
    
    def voir_historique(self, instance):
        self.manager.current = 'historique'
    
    def config_email(self, instance):
        self.manager.current = 'config'


class FormulaireScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'formulaire'
        self.photos = []
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # En-tête avec bouton retour
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_retour = Button(text='← Retour', size_hint_x=0.3)
        btn_retour.bind(on_press=self.retour_accueil)
        header.add_widget(btn_retour)
        header.add_widget(Label(text='Nouveau Rapport', font_size='18sp'))
        main_layout.add_widget(header)
        
        # Formulaire avec scroll
        form_layout = GridLayout(cols=2, spacing=5, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Champs du formulaire
        champs = [
            ('Client:', 'client'),
            ('Adresse:', 'adresse'),
            ('Date Installation:', 'date'),
            ('Technicien:', 'technicien'),
            ('Type Équipement:', 'equipement'),
            ('Numéro Série:', 'serie'),
            ('Observations:', 'observations')
        ]
        
        self.inputs = {}
        
        for label_text, key in champs:
            label = Label(text=label_text, size_hint_y=None, height='40dp')
            if key == 'observations':
                text_input = TextInput(
                    multiline=True,
                    size_hint_y=None,
                    height='100dp'
                )
            elif key == 'date':
                text_input = TextInput(
                    text=datetime.datetime.now().strftime('%Y-%m-%d'),
                    size_hint_y=None,
                    height='40dp'
                )
            else:
                text_input = TextInput(size_hint_y=None, height='40dp')
            
            self.inputs[key] = text_input
            form_layout.add_widget(label)
            form_layout.add_widget(text_input)
        
        main_layout.add_widget(form_layout)
        
        # Section photos
        photo_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        
        photo_header = BoxLayout(size_hint_y=0.3)
        photo_header.add_widget(Label(text='Photos:', font_size='16sp'))
        
        btn_photo = Button(text='📷 Prendre Photo', size_hint_x=0.5)
        btn_photo.bind(on_press=self.prendre_photo)
        photo_header.add_widget(btn_photo)
        
        photo_layout.add_widget(photo_header)
        
        # Liste des photos
        self.photo_list = Label(text='Aucune photo', size_hint_y=0.7)
        photo_layout.add_widget(self.photo_list)
        
        main_layout.add_widget(photo_layout)
        
        # Boutons d'action
        action_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        btn_sauver = Button(text='💾 Sauvegarder', background_color=(0.3, 0.7, 0.3, 1))
        btn_sauver.bind(on_press=self.sauvegarder_rapport)
        
        btn_envoyer = Button(text='📧 Envoyer par Email', background_color=(0.2, 0.6, 1, 1))
        btn_envoyer.bind(on_press=self.envoyer_rapport)
        
        action_layout.add_widget(btn_sauver)
        action_layout.add_widget(btn_envoyer)
        
        main_layout.add_widget(action_layout)
        
        self.add_widget(main_layout)
    
    def retour_accueil(self, instance):
        self.manager.current = 'accueil'
    
    def prendre_photo(self, instance):
        self.manager.current = 'camera'
    
    def ajouter_photo(self, chemin_photo):
        self.photos.append(chemin_photo)
        self.mettre_a_jour_liste_photos()
    
    def mettre_a_jour_liste_photos(self):
        if self.photos:
            text = f"{len(self.photos)} photo(s) ajoutée(s)"
        else:
            text = "Aucune photo"
        self.photo_list.text = text
    
    def sauvegarder_rapport(self, instance):
        rapport_data = self.collecter_donnees()
        
        # Créer le dossier rapports s'il n'existe pas
        if not os.path.exists('rapports'):
            os.makedirs('rapports')
        
        # Nom du fichier avec timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_fichier = f'rapport_{timestamp}.json'
        
        try:
            with open(f'rapports/{nom_fichier}', 'w', encoding='utf-8') as f:
                json.dump(rapport_data, f, ensure_ascii=False, indent=2)
            
            self.afficher_popup('Succès', 'Rapport sauvegardé avec succès!')
        except Exception as e:
            self.afficher_popup('Erreur', f'Erreur lors de la sauvegarde: {str(e)}')
    
    def collecter_donnees(self):
        return {
            'date_creation': datetime.datetime.now().isoformat(),
            'client': self.inputs['client'].text,
            'adresse': self.inputs['adresse'].text,
            'date_installation': self.inputs['date'].text,
            'technicien': self.inputs['technicien'].text,
            'equipement': self.inputs['equipement'].text,
            'numero_serie': self.inputs['serie'].text,
            'observations': self.inputs['observations'].text,
            'photos': self.photos
        }
    
    def generer_pdf(self, donnees):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_pdf = f'rapport_{timestamp}.pdf'
        
        try:
            doc = SimpleDocTemplate(nom_pdf, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centré
            )
            story.append(Paragraph("RAPPORT D'INSTALLATION", title_style))
            
            # Informations générales
            story.append(Spacer(1, 12))
            
            infos = [
                f"<b>Client:</b> {donnees['client']}",
                f"<b>Adresse:</b> {donnees['adresse']}",
                f"<b>Date d'installation:</b> {donnees['date_installation']}",
                f"<b>Technicien:</b> {donnees['technicien']}",
                f"<b>Équipement:</b> {donnees['equipement']}",
                f"<b>Numéro de série:</b> {donnees['numero_serie']}"
            ]
            
            for info in infos:
                story.append(Paragraph(info, styles['Normal']))
                story.append(Spacer(1, 6))
            
            # Observations
            if donnees['observations']:
                story.append(Spacer(1, 12))
                story.append(Paragraph("<b>Observations:</b>", styles['Heading2']))
                story.append(Paragraph(donnees['observations'], styles['Normal']))
            
            # Photos
            if donnees['photos']:
                story.append(Spacer(1, 12))
                story.append(Paragraph("<b>Photos:</b>", styles['Heading2']))
                
                for i, photo_path in enumerate(donnees['photos']):
                    if os.path.exists(photo_path):
                        try:
                            img = RLImage(photo_path, width=4*inch, height=3*inch)
                            story.append(img)
                            story.append(Paragraph(f"Photo {i+1}", styles['Caption']))
                            story.append(Spacer(1, 12))
                        except:
                            story.append(Paragraph(f"Photo {i+1}: Erreur de chargement", styles['Normal']))
            
            doc.build(story)
            return nom_pdf
            
        except Exception as e:
            print(f"Erreur génération PDF: {e}")
            return None
    
    def envoyer_rapport(self, instance):
        rapport_data = self.collecter_donnees()
        
        # Générer le PDF
        nom_pdf = self.generer_pdf(rapport_data)
        
        if nom_pdf:
            # Proposer les méthodes d'envoi
            self.choisir_methode_envoi(nom_pdf, rapport_data)
        else:
            self.afficher_popup('Erreur', 'Erreur lors de la génération du PDF')
    
    def choisir_methode_envoi(self, nom_pdf, rapport_data):
        """Popup pour choisir la méthode d'envoi"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        content.add_widget(Label(text='Comment voulez-vous envoyer le rapport?', size_hint_y=0.3))
        
        # Bouton Email par défaut
        btn_email_defaut = Button(text='📧 App Email par défaut', size_hint_y=0.2)
        btn_email_defaut.bind(on_press=lambda x: self.envoyer_email_defaut(nom_pdf, rapport_data))
        content.add_widget(btn_email_defaut)
        
        # Bouton SMTP configuré
        btn_smtp = Button(text='⚙️ SMTP configuré', size_hint_y=0.2)
        btn_smtp.bind(on_press=lambda x: self.envoyer_smtp(nom_pdf, rapport_data))
        content.add_widget(btn_smtp)
        
        # Bouton Annuler
        btn_annuler = Button(text='❌ Annuler', size_hint_y=0.2)
        
        popup = Popup(
            title='Méthode d\'envoi',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        btn_annuler.bind(on_press=popup.dismiss)
        content.add_widget(btn_annuler)
        
        popup.open()
    
    def envoyer_email_defaut(self, nom_pdf, rapport_data):
        """Ouvre l'application email par défaut avec le rapport"""
        try:
            # Créer le sujet et le corps de l'email
            sujet = f"Rapport d'installation - {rapport_data['client']}"
            
            corps = f"""Bonjour,
            
Veuillez trouver ci-joint le rapport d'installation pour :

Client: {rapport_data['client']}
Adresse: {rapport_data['adresse']}
Date d'installation: {rapport_data['date_installation']}
Technicien: {rapport_data['technicien']}
Équipement: {rapport_data['equipement']}

Cordialement
"""
            
            # Chemin complet du fichier PDF
            chemin_pdf = os.path.abspath(nom_pdf)
            
            # Méthode selon l'OS
            systeme = platform.system()
            
            if systeme == "Windows":
                # Windows - utilise mailto: avec attachment
                self.ouvrir_email_windows(sujet, corps, chemin_pdf)
            elif systeme == "Darwin":  # macOS
                self.ouvrir_email_mac(sujet, corps, chemin_pdf)
            else:  # Linux
                self.ouvrir_email_linux(sujet, corps, chemin_pdf)
                
        except Exception as e:
            self.afficher_popup('Erreur', f'Erreur ouverture email: {str(e)}\n\nFichier PDF créé: {nom_pdf}')
    
    def ouvrir_email_windows(self, sujet, corps, chemin_pdf):
        """Ouvre l'email par défaut sur Windows"""
        try:
            # Encoder les paramètres pour l'URL
            sujet_encode = urllib.parse.quote(sujet)
            corps_encode = urllib.parse.quote(corps)
            
            # Créer l'URL mailto
            url_mailto = f"mailto:?subject={sujet_encode}&body={corps_encode}"
            
            # Ouvrir l'email par défaut
            os.startfile(url_mailto)
            
            # Message d'info avec le chemin du PDF
            self.afficher_popup('Email ouvert', 
                f'Application email ouverte!\n\nAjoutez manuellement le fichier:\n{chemin_pdf}\n\nOu glissez-déposez le PDF dans l\'email.')
            
        except Exception as e:
            # Alternative : ouvrir juste le dossier contenant le PDF
            try:
                os.startfile(os.path.dirname(chemin_pdf))
                self.afficher_popup('Dossier ouvert', 
                    f'Le PDF est prêt dans le dossier ouvert.\n\nFichier: {os.path.basename(chemin_pdf)}')
            except:
                self.afficher_popup('PDF créé', f'PDF créé: {chemin_pdf}')
    
    def ouvrir_email_mac(self, sujet, corps, chemin_pdf):
        """Ouvre l'email par défaut sur macOS"""
        try:
            # Utiliser AppleScript pour ouvrir Mail avec pièce jointe
            script = f'''
            tell application "Mail"
                activate
                set newMessage to make new outgoing message
                tell newMessage
                    set subject to "{sujet}"
                    set content to "{corps}"
                    make new attachment with properties {{file name:POSIX file "{chemin_pdf}"}}
                end tell
                set visible of newMessage to true
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            self.afficher_popup('Email ouvert', 'Email préparé dans Mail avec le PDF attaché!')
            
        except Exception as e:
            # Alternative simple
            url_mailto = f"mailto:?subject={urllib.parse.quote(sujet)}&body={urllib.parse.quote(corps)}"
            webbrowser.open(url_mailto)
            self.afficher_popup('Email ouvert', f'Ajoutez le PDF: {chemin_pdf}')
    
    def ouvrir_email_linux(self, sujet, corps, chemin_pdf):
        """Ouvre l'email par défaut sur Linux"""
        try:
            # Essayer xdg-email (plus moderne)
            cmd = [
                'xdg-email',
                '--subject', sujet,
                '--body', corps,
                '--attach', chemin_pdf
            ]
            subprocess.run(cmd, check=True)
            self.afficher_popup('Email ouvert', 'Email préparé avec le PDF attaché!')
            
        except:
            try:
                # Alternative avec mailto
                url_mailto = f"mailto:?subject={urllib.parse.quote(sujet)}&body={urllib.parse.quote(corps)}"
                webbrowser.open(url_mailto)
                self.afficher_popup('Email ouvert', f'Ajoutez le PDF: {chemin_pdf}')
            except Exception as e:
                self.afficher_popup('Erreur', f'Erreur: {str(e)}\nPDF créé: {chemin_pdf}')
    
    def envoyer_smtp(self, nom_pdf, rapport_data):
        """Envoi par SMTP configuré (ancienne méthode)"""
        try:
            # Charger la config SMTP
            if not os.path.exists('config_email.json'):
                self.afficher_popup('Configuration manquante', 
                    'Configurez d\'abord les paramètres SMTP dans "Configuration Email"')
                return
            
            with open('config_email.json', 'r') as f:
                config = json.load(f)
            
            # Vérifier les champs requis
            champs_requis = ['smtp_server', 'smtp_port', 'email', 'password', 'destinataire']
            for champ in champs_requis:
                if not config.get(champ):
                    self.afficher_popup('Configuration incomplète', 
                        f'Le champ "{champ}" est manquant dans la configuration.')
                    return
            
            # Créer le message email
            msg = MIMEMultipart()
            msg['From'] = config['email']
            msg['To'] = config['destinataire']
            msg['Subject'] = f"Rapport d'installation - {rapport_data['client']}"
            
            # Corps du message
            corps = f"""Bonjour,

Veuillez trouver ci-joint le rapport d'installation pour :

Client: {rapport_data['client']}
Adresse: {rapport_data['adresse']}
Date d'installation: {rapport_data['date_installation']}
Technicien: {rapport_data['technicien']}
Équipement: {rapport_data['equipement']}

Cordialement
"""
            msg.attach(MIMEText(corps, 'plain', 'utf-8'))
            
            # Ajouter la pièce jointe PDF
            if os.path.exists(nom_pdf):
                with open(nom_pdf, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(nom_pdf)}'
                )
                msg.attach(part)
            
            # Envoyer l'email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['email'], config['password'])
            server.send_message(msg)
            server.quit()
            
            self.afficher_popup('Succès', 'Email envoyé avec succès!')
            
        except Exception as e:
            self.afficher_popup('Erreur SMTP', f'Erreur envoi SMTP: {str(e)}')
    
    def afficher_popup(self, titre, message):
        popup = Popup(
            title=titre,
            content=Label(text=message, text_size=(300, None)),
            size_hint=(0.8, 0.6)
        )
        popup.open()


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'camera'
        
        layout = BoxLayout(orientation='vertical')
        
        # En-tête
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_retour = Button(text='← Retour', size_hint_x=0.3)
        btn_retour.bind(on_press=self.retour_formulaire)
        header.add_widget(btn_retour)
        header.add_widget(Label(text='Prendre une Photo'))
        layout.add_widget(header)
        
        # Caméra avec gestion d'erreur
        try:
            self.camera = Camera(play=False, resolution=(640, 480))
            layout.add_widget(self.camera)
            self.camera_available = True
        except Exception as e:
            # Si la caméra ne fonctionne pas, afficher un message
            error_label = Label(
                text=f'Caméra non disponible\n\nErreur: {str(e)}\n\nInstallez OpenCV:\npip install opencv-python',
                text_size=(None, None)
            )
            layout.add_widget(error_label)
            self.camera = None
            self.camera_available = False
        
        # Boutons
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        btn_capture = Button(text='📷 Capturer')
        btn_capture.bind(on_press=self.capturer_photo)
        
        # Bouton alternatif si pas de caméra
        if not self.camera_available:
            btn_capture.text = '📁 Choisir image'
            btn_capture.bind(on_press=self.choisir_image)
        
        btn_annuler = Button(text='❌ Annuler')
        btn_annuler.bind(on_press=self.retour_formulaire)
        
        btn_layout.add_widget(btn_capture)
        btn_layout.add_widget(btn_annuler)
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        if self.camera_available and self.camera:
            self.camera.play = True
    
    def on_leave(self):
        if self.camera_available and self.camera:
            self.camera.play = False
    
    def retour_formulaire(self, instance):
        self.manager.current = 'formulaire'
    
    def capturer_photo(self, instance):
        if not self.camera_available:
            self.choisir_image(instance)
            return
            
        # Créer le dossier photos s'il n'existe pas
        if not os.path.exists('photos'):
            os.makedirs('photos')
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_photo = f'photos/photo_{timestamp}.png'
        
        try:
            self.camera.export_to_png(nom_photo)
            
            # Ajouter la photo au formulaire
            formulaire_screen = self.manager.get_screen('formulaire')
            formulaire_screen.ajouter_photo(nom_photo)
            
            # Retourner au formulaire
            self.retour_formulaire(None)
            
        except Exception as e:
            popup = Popup(
                title='Erreur',
                content=Label(text=f'Erreur lors de la capture: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def choisir_image(self, instance):
        """Alternative : choisir une image existante"""
        popup = Popup(
            title='Info',
            content=Label(text='Fonctionnalité de sélection d\'image\nà implémenter.\n\nPour l\'instant, installez OpenCV:\npip install opencv-python'),
            size_hint=(0.8, 0.5)
        )
        popup.open()


class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'config'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # En-tête
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_retour = Button(text='← Retour', size_hint_x=0.3)
        btn_retour.bind(on_press=self.retour_accueil)
        header.add_widget(btn_retour)
        header.add_widget(Label(text='Configuration Email', font_size='18sp'))
        layout.add_widget(header)
        
        # Formulaire de configuration
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.7)
        
        # Champs de configuration
        self.config_inputs = {}
        champs_config = [
            ('Serveur SMTP:', 'smtp_server'),
            ('Port:', 'smtp_port'),
            ('Votre Email:', 'email'),
            ('Mot de passe:', 'password'),
            ('Email destinataire:', 'destinataire')
        ]
        
        for label_text, key in champs_config:
            label = Label(text=label_text)
            if key == 'password':
                text_input = TextInput(password=True)
            elif key == 'smtp_port':
                text_input = TextInput(text='587')
            elif key == 'smtp_server':
                text_input = TextInput(text='smtp.gmail.com')
            else:
                text_input = TextInput()
            
            self.config_inputs[key] = text_input
            form_layout.add_widget(label)
            form_layout.add_widget(text_input)
        
        layout.add_widget(form_layout)
        
        # Boutons
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        btn_sauver = Button(text='💾 Sauvegarder Config')
        btn_sauver.bind(on_press=self.sauver_config)
        
        btn_test = Button(text='✉️ Test Email')
        btn_test.bind(on_press=self.tester_email)
        
        btn_layout.add_widget(btn_sauver)
        btn_layout.add_widget(btn_test)
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
        
        # Charger la config existante
        self.charger_config()
    
    def retour_accueil(self, instance):
        self.manager.current = 'accueil'
    
    def sauver_config(self, instance):
        config = {
            'smtp_server': self.config_inputs['smtp_server'].text,
            'smtp_port': int(self.config_inputs['smtp_port'].text or 587),
            'email': self.config_inputs['email'].text,
            'password': self.config_inputs['password'].text,
            'destinataire': self.config_inputs['destinataire'].text
        }
        
        try:
            with open('config_email.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            popup = Popup(
                title='Succès',
                content=Label(text='Configuration sauvegardée!'),
                size_hint=(0.6, 0.4)
            )
            popup.open()
        except Exception as e:
            popup = Popup(
                title='Erreur',
                content=Label(text=f'Erreur: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def charger_config(self):
        try:
            if os.path.exists('config_email.json'):
                with open('config_email.json', 'r') as f:
                    config = json.load(f)
                
                for key, value in config.items():
                    if key in self.config_inputs:
                        self.config_inputs[key].text = str(value)
        except:
            pass
    
    def tester_email(self, instance):
        popup = Popup(
            title='Test Email',
            content=Label(text='Fonctionnalité de test à implémenter'),
            size_hint=(0.6, 0.4)
        )
        popup.open()


class HistoriqueScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'historique'
        
        layout = BoxLayout(orientation='vertical', padding=10)
        
        # En-tête
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_retour = Button(text='← Retour', size_hint_x=0.3)
        btn_retour.bind(on_press=self.retour_accueil)
        header.add_widget(btn_retour)
        header.add_widget(Label(text='Historique des Rapports', font_size='18sp'))
        layout.add_widget(header)
        
        # Liste des rapports
        self.liste_rapports = Label(text='Chargement...', size_hint_y=0.9)
        layout.add_widget(self.liste_rapports)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.charger_historique()
    
    def retour_accueil(self, instance):
        self.manager.current = 'accueil'
    
    def charger_historique(self):
        try:
            if os.path.exists('rapports'):
                fichiers = os.listdir('rapports')
                fichiers_json = [f for f in fichiers if f.endswith('.json')]
                
                if fichiers_json:
                    historique_text = f"Rapports trouvés: {len(fichiers_json)}\n\n"
                    for fichier in sorted(fichiers_json, reverse=True):
                        historique_text += f"• {fichier}\n"
                else:
                    historique_text = "Aucun rapport trouvé"
            else:
                historique_text = "Dossier rapports inexistant"
            
            self.liste_rapports.text = historique_text
            
        except Exception as e:
            self.liste_rapports.text = f"Erreur: {str(e)}"


class RapportInstallationApp(App):
    def build(self):
        # Créer le gestionnaire d'écrans
        sm = ScreenManager()
        
        # Ajouter tous les écrans
        sm.add_widget(AccueilScreen())
        sm.add_widget(FormulaireScreen())
        sm.add_widget(CameraScreen())
        sm.add_widget(ConfigScreen())
        sm.add_widget(HistoriqueScreen())
        
        return sm


if __name__ == '__main__':
    RapportInstallationApp().run()
