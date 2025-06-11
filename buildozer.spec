[app]

# (str) Titre de votre application
title = Rapport Installation

# (str) Nom du package
package.name = rapportinstallation

# (str) Domaine du package (utilisé pour créer android.manifest)
package.domain = org.example

# (str) Fichier source principal de votre application
source.main = main.py

# (str) Version de l'application
version = 1.0

# (list) Modèles d'application à inclure dans l'APK
#requirements = python3,kivy,reportlab,pillow

# Version complète des requirements
requirements = python3,kivy==2.1.0,reportlab,pillow,plyer,opencv

# (str) Icône de l'application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Architectures supportées
#android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Journal niveau de log (0 = seulement erreur, 1 = info, 2 = debug)
log_level = 2

# (int) Afficher les avertissements en utilisant la couleur (0 = Off, 1 = On)
warn_on_root = 1


[android]

# (str) Chemin vers Android SDK
#android.sdk_path = 

# (str) Chemin vers Android NDK
#android.ndk_path = 

# (str) Version de l'API Android à utiliser
android.api = 31

# (str) Version minimum de l'API
android.minapi = 21

# (str) Version du NDK Android à utiliser
android.ndk = 25b

# (bool) Utiliser --private storage (True) ou --dir storage (False)
android.private_storage = True

# (str) Version du NDK Python à utiliser
#android.ndk_python = python3

# (str) Nom du répertoire contenant l'ensemble des fichiers Java
#android.java_src_dirs = src/java

# (list) Modèles Java à ajouter
#android.java_classes = 

# (str) Fichier AAR à ajouter
#android.aar_dirs = 

# (str) Fichier gradle dependencies à ajouter
#android.gradle_dependencies = 

# (list) Permissions Java à ajouter
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA

# (str) Le bootstrap Android à utiliser
#android.bootstrap = sdl2

# (str) Argument à passer au bootstrap
#android.bootstrap_args = 

# (str) XML à inclure pour le manifest
#android.manifest_placeholders = 

# (str) Icône de l'application (remplace icon.filename si défini)
#android.icon = 

# (str) Répertoire de ressources Android
#android.res_dirs = res

# (str) Chemin vers un fichier build.gradle personnalisé
#android.custom_gradle = 

# (str) Chemin vers un fichier build.xml personnalisé
#android.build_xml = 

# (str) Chemin vers un fichier gradle.properties personnalisé
#android.gradle_properties = 

# (str) Chemin vers un fichier local.properties personnalisé
#android.local_properties = 

# (str) Nom du fichier de configuration Proguard
#android.proguard = 

# (str) Le mode de signature de l'APK ('debug' ou 'release')
android.release_mode = debug

# (str) Format de fichier APK ('apk' ou 'aab')
android.release_format = apk

# (str) Le keystore à utiliser pour signer l'APK
#android.keystore = 

# (str) Le nom de l'alias de la clé dans le keystore
#android.keyalias = 

# (str) Le DN du certificat
#android.cert_dn = 

# (str) Chemin vers le fichier de mot de passe du keystore
#android.keystore_passwd = 

# (str) Chemin vers le fichier de mot de passe de l'alias
#android.keyalias_passwd = 

# (bool) Activer la vérification multi-dex
#android.enable_multidex = 


[ios]

# (str) Chemin vers les outils de développement iOS
#ios.codesign_debug = 

# (str) Certificat de signature pour la version de débogage
#ios.codesign_release = 

[buildozer:virtualenv]

# (str) Version de Python à utiliser
#python = python3.8