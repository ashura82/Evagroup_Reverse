# Installation et déploiement de l'environement NGINX + API FLASK

1. Introduction:

Ce repository permet de déployer un serveur avec les fonctionnalitées suivantes :

    * Un serveur nginx proxy-pass avec gestion https

    * Un firewall CSF pour la gestion des règles
    
    * Une API en python permettant de surveiller les métriques du serveur, et configurer nginx et CSF

2. Détails des dossiers & fichiers:
  
   * **certificat** - Contient le script qui va nous générer les certificats HTTPS pour les sites webs
   
   * **docs** - Contient les documentations de CSF
   
   * **ressources** - Contient l'environnement virtuel nécessaire à l'api

   * **script** - Contient les scripts de configuration.
   
   
    
 
# ConfigServer Security & Firewall

**ConfigServer Security & Firewall (CSF)** est un pare-feu de type filtre de paquets dynamique. C'est aussi une application de sécurité et de détection des connexions et intrusions conçue pour les serveurs Linux. Il s’agit d’un outil de sécurité qui peut protéger votre serveur contre des attaques, et ainsi améliorer la sécurité de votre serveur.


## Installation automatisée

L'installation du pare-feu dans notre solution est automatisée dans le script d'installation du reverse proxy. Les informations d'environnement du serveur sont envoyées automatiquement à la base de données. Les fichiers de configurations sont poussés a l'installation.


## Gestion du pare-feu

La gestion du pare-feu et du cluster s'effectue depuis l'interface de gestion du reverse proxy. Vous trouverez les informations pour redémarrer les services, rechercher/Blacklister ou Whitelister des IP dans le README du Repositorie **ashura82/Evagroup_GUI**.


## Clustering

Afin d'automatiser le déploiement de plusieurs serveurs reverse proxy, notre solution exploite la **fonction de clustering** de CSF. Le serveur de base de données modifie de manière automatisée à l'intégration d'un nouveau membre les fichiers de configurations de tous les autres membres du cluster.


## Configuration mise en place

Une configuration recommandée est mise en place automatiquement via le fichier **/etc/csf/csf.conf**. Vous trouverez les informations pour le modifier et le mettre a jour dans le README du Repositorie **ashura82/Evagroup_BDD**.
Cette configuration intègre la détection des actions telles que le scan de port, l'icmp flood, l'udp flood, les attaques distribuées, etc.


## Blocage d'IP malveillantes

Une base d'IP malveillante est mise en place automatique via le fichier **/etc/csf/csf.blocklists**. Vous trouverez les informations pour le modifier et le mettre a jour dans le README du Repositorie **ashura82/Evagroup_BDD**.


## Documentations

Dans le dossier /docs de ce repositorie vous trouverez les fichiers readme.txt et reset_to_defaults.conf qui expliquent les fonctionnalités du pare-feu vous permettant d'en modifier la configuration.
