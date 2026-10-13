POKER NIGHT — MULTIJOUEUR EN LIGNE

Contenu :
- index.html : design Casino Prestige iPad, sons et règles d'origine, avec synchronisation
- server.py : serveur Python multijoueur sans bibliothèque supplémentaire

TEST SUR ORDINATEUR :
1. Installe Python 3 si nécessaire.
2. Ouvre un terminal dans ce dossier.
3. Lance : python server.py
4. Ouvre http://localhost:8000 dans ton navigateur.
5. Clique sur « Créer un salon », puis partage le code.

POUR JOUER À DISTANCE :
Il faut héberger ce dossier sur un serveur qui exécute Python (par exemple un VPS
ou un hébergement prenant en charge les applications Python persistantes).
Commande de démarrage : python server.py
Variable d'environnement PORT facultative (défaut 8000).
Active HTTPS via ton hébergeur ou un reverse proxy.
Ne publie PAS seulement index.html sur un hébergement statique : la
synchronisation nécessite server.py.

ATTENTION :
- Chaque personne peut piloter les mises et attribuer les pots.
- Le serveur sauvegarde les salons dans salons.json, sur son disque local.
- En cas de deux actions exactement simultanées, la dernière personne dont
  la modification est refusée doit recommencer son action après synchronisation.
- Ceci est un tableau de suivi entre amis, pas une plateforme de paris en argent réel.
- Les salons n'ont pas de mot de passe : partage le code uniquement avec tes amis.
