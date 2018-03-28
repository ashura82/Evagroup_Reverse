# Présentation

Script bash permettant la mise en place de certificat qui authentifie le client sur un site hebergé derrière notre reverse proxy

## Avant de commencer

Ces instructions vous permettront d'obtenir une copie du projet opérationnel sur votre machine locale à des fins de développement et de test. Voir déploiement pour les notes sur la façon de déployer le projet sur un système actif.

### Prèrequis

Pour executer ce script, il faudra necessairement auparavant que le fichier vhost soit configurer sur nginx dans /sites-available/nomdudomaine


```
/etc/nginx/sites-available/wordpress3
```

### Execute

Le script se déroule en trois étapes :

Etape une, demande du nom de domaine à l'utilisateur, puis création du dossier où les certificats vont être générés.

```
read -p "Entrez le nom de domaine : " domain

mkdir /cert-$domain

cd /cert-$domain
```

Seconde etape, la génération du certificat serveur qui va nous servir à signé le certificat client qui va aussi êter généré ici

```
# Create the CA Key and Certificate for signing Client Certs
openssl genrsa -des3 -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Create the Server Key, CSR, and Certificate
openssl genrsa -des3 -out server.key 1024
openssl req -new -key server.key -out server.csr

# We're self signing our own server cert here.  This is a no-no in production.
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

# Create the Client Key and CSR
openssl genrsa -des3 -out client.key 1024
openssl req -new -key client.key -out client.csr

# Sign the client certificate with our CA cert.  Unlike signing our own server cert, this is what we want to do.
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt

# Generation du fichier .p12 
openssl pkcs12 -export -clcerts -in /cert-$domain/client.crt -inkey /cert-$domain/client.key -out /cert-$domain/c$
```

Troisième et dernière étape, echo du texte à ajouter dans le fichier vhost de nginx ainsi que la consigne pour récuperer les certificats à importer dans le naviguateur

```
echo "texte à ajouter dans le fichier /etc/nginx/sites-available/$domain
                ssl_client_certificate /cert-$domain/ca.crt;          
                ssl_verify_client on;"

echo récuperer ensuite via scp ou autre le certificat généré qui se trouve dans /cert-$domain et les intégrer au naviguateur.
```

## Test

Aller dans votre naviguateur, ajouter le ca.crt dans "Autorités", puis le fichier client.p12 dans "Vos certificats".

Une fois sur le site, un pop-up devrait vous demander le certificat à selectionner pour le présenter au serveur.


## Deploiement

lancez le script en sudo pour ne pas avoir de problèmes de droits.


## Authors

* **Mantes Julien** - *Initial work*

Voir aussi la liste des [contributors](https://github.com/ashura82) qui ont participer au projet.



