
### generation certificat client ###

read -p "Entrez le nom de domaine : " domain

mkdir /cert-$domain

cd /cert-$domain

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
 

echo "texte à ajouter dans le fichier /etc/nginx/sites-available/$domain"
echo "ssl_client_certificate /cert-$domain/ca.crt;"          
echo "ssl_verify_client on;"

echo récuperer ensuite via scp ou autre le certificat généré qui se trouve dans /cert-$domain et les intégrer au naviguateur 
