# Installation et déploiement de l'environement NGINX + API FLASK

1. Introduction:

Ce repository permet de déployer un serveur avec les fonctionnalitées suivantes :

    * Un serveur nginx proxy-pass avec gestion https

    * Un firewall CSF pour la gestion des règles
    
    * Une API en python permettant de surveiller les métriques du serveur, et configurer nginx et CSF

2. Détails des dossiers & fichiers:
  
   * **certificat** - Contient le script qui va nous générer les certificats HTTPS pour les sites webs
   
   * **docs** - Contient la configuration de csf
   
   * **ressources** - Contient l'environnement virtuel nécessaire à l'api

   * **script** - Contient les scripts de configuration.