# pierre_feuille_ciseaux en reseaux

1) Utilisation 
  
  a) mode serveur : 
      
      ./serveur.py

  b)mode client : 
       
       ./client.py
       
       choix possible : pierre , feuille ,ciseaux 
       


2) Organisation

  
  a) Organisation génerale
     
     le module client.py contient le code du client, le module serveur.py contient le code mode serveur, le module hash.py   contient la fonction de hashage utilisée par les client, cette fonction permet de checker les choix de chaque client en évitant la triche.
     
  b) Organisation du module client.py 
     
     -La fonction udp_msg recois le msg udp du serveur qui permet de savoir le nombre de place disponible dans la partie.
     
     -La fonction interact-s se connect au serveur après avoir reçu l'udp, envois le numéro de port de notre client au  serveur puis reçois le nombre de joueurs qui se sont connectés avant nous et reçois leurs addresses les unes à la suite       des autres. puis cette fonction retourne les adresse recus par le serveur.
     
     -La fonction extract_addr permet l'extraction et la conversion des bytes representant l'ip et le port en ascii et elle   renvois une listes avec les addresses ip/port des autres clients.
     
     -La fonction genère joueurs se connecte à chaque joueur et accepte les connexions des autres joueurs qui se sont         connectés au serveur après nous. puis elle renvois une liste des sockets des tous les joueurs de la partie.
     
     -La fonction genère-hash genere la hash comme décrit dans le protcole l'envois aux autres joueurs et reçois pendant un   delais de 5 secondes le hash des autres joueurs.
     
     -La fonction verification verifie l'exactitude du hash et genere les resultats.
     
     -La fonction check-result selon les resultat elle calcule les gagnant et les perdants dans la partie. elle renvois au   main des numeros qui permettent de connaitre les gagnants et les perdant puis, si on a perdu on ferme toutes les             sockets avec les autres clients.si on a gagné et qu'il y a des perdants on ferme les sockets avec ces clients perdants       et on décremente le nombre de joueurs restant et on reprend la partie avec les gagnants.
  
  c) Organisation du module serveur
     
     Le serveur envois le msg udp sur le reseaux, comme décrit dans le protocole, jusqu'a a ce qu'il ny ait plus de places   disponilbes(spécifié par l'utilisateur), a chaque tentative de connexions au serveur par le client, le serveur lui            envois le nombre de joueurs ayant joint la partie, puis le client lui repond en retour par son port, ensuite le serveur      envois à ce client les addresse des joueurs qui se sont connectés avant lui si il y en a. si le nombre de place              disponible atteint zéro, le serveur se deconnecte. et la partie commence entre les clients
     
     Pour plus de details voir le protocole.
     
3) difficultées rencontrées durant le projet 
  
        problème durant la conversion du hash de int en bytes pour l'envoyer, ce qui ne fonctionnait pas avec les clients des autres langages.
        
     
     
  
     
       
   

