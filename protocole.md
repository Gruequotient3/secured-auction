# Plateforme de vente / achat par enchères

## Membres du groupe D
- Anparasan ANPUKKODY
- Clément LEVASTRE
- Gaëtan ROLLIN
- Mykyta KOPYLOV
- Ethan SAMAMA-VAUTRIN

## Environnement

### Langages/outils:
Serveur : Python - Bottle, Flask, FastAPI (indécidé)

Client : HTML/CSS/JS

Base de données : SQL

## Sécurité

### Informations chiffrées
- Proposition de vente / réponse
- Pseudo
- Gagnant

### Informations non chiffrées
- Informations des objets à vendre
- Dernière enchère

### Attaques potentielles
- Envoie de faux messages de gagnant à une vente (signature)
- Fausse mise (signature)
- Intégrité du message

## Serveur

### Résumé

Ce projet consiste à implémenter la gestion d'une enchère d'un ou plusieurs objets.
Pour simuler une enchère, un système de compte sera mis en place avec un identifiant et un mot de passe.<br/>
Ce compte permettra aussi de contenir le solde du client. 
Pour des raisons évidentes, nous n'allons pas utiliser nos vrais comptes bancaire mais un solde d'argent, qui pourra être alimenter pour les démonstrations.<br/>
L'enchère se déroulera de la manière suivante :
- Une enchère est créé par le serveur. Dans les futures implémentations, le client pourra créer une enchère.
- Le timer commence et les clients peuvent enchèrir.
- Un client ayant fait une enchère à la possibilité d'enlever son enchère pendant 10 secondes.
- Une fois le temps écoulé, l'objet est par la dernière personne qui a enchéri.

### Règles / déroulement
- Création d'un compte
- Gestion de qui peut enchérir (tout le monde)
- Lancer une enchère (prix de base, objet(image, titre, description), temps limite)
- Pas d'envoi au moment de l'ajout, simplement lorsque la demande est demandé
- Participer à une enchère (nouveau prix)
- Impossibilité d'enchèrir à un prix inférieur à la dernière enchère ou au prix de base
- Temps de désistement (10 secondes)
- Vendeur ne peut pas enchérir
- Peut pas enchérir si dernier bidder (problème avec désistement)
- (Proposition) Permettre de mettre fin à l'enchère plus tôt si le prix atteint convient au vendeur

## Protocole

### Générales
```
srv : ERROR 00 — Erreur serveur  
srv : ERROR 10 — Commande invalide  
srv : ERROR 11 — Argument invalide  
srv : ERROR 12 — Action non autorisée  
srv : ERROR 13 — Non identifié  
```


### Identification
```
clt : AUTHN <pseudo> <motdepasse>

srv : AUTHN <pseudo> OK
srv : ERROR 20 // Authentification échouée
srv : ERROR 21 // Compte déjà connecté
```

### Création de compte
```
clt : CREAT <pseudo> <motdepasse>

srv : CREAT OK
srv : ERROR 23 // Pseudo déjà utilisé
srv : ERROR 24 // Mot de passe pas assez fort
```

### Créditer le compte :
```
clt : CREDIT <montant>

srv : CREDIT <montant>
srv : ERROR 25 // Montant invalide
```

### Création d'une enchère :
```
clt : NAUCT <titre> <prix_base> <temps_limite>

srv : NAUCT <id_enchere> <titre> <prix_base> <temps_limite>
srv : ERROR 30 // Temps incorrect
srv : ERROR 31 // Prix incorrect
srv : ERROR 32 // Titre incorrect (nb caractères, ...)
```

### Enchérir :
```
clt : BDAUC (<id_compte>) <id_enchere> <montant>

srv : BDAUC <id_enchere> <montant>
srv : ERROR 33 // Id_enchere incorrect
srv : ERROR 31 // Prix incorrect
srv : ERROR 37 // Impossible d'enchérir
srv : ERROR 26 // Crédit insuffisant
```

### Annulation d'enchérissement :
```
clt : CNBID <id_enchere>

srv : CNBID <id_enchere> <montant>
srv : ERROR 33 // Id_enchere incorrect
srv : ERROR 34 // Temps de désisitement écoulé
srv : ERROR 35 // Enchérissement plus valide
srv : ERROR 36 // Aucune mise
```

### Fin d'enchère :
```
srv : EDAUC <id_enchere> <montant> (participant; si pas d'enchérisseur, renvoi 0 pour le montant)
srv : WNAUC <id_enchere> <montant> (gagnant de l'enchère)
```

### Liste des enchères :
```
clt : LSAUC

srv : LSAUC [<id_enchere1>; <id_encheren>...] [<titre_enchere1>; <titre_encheren>...] [<id_img1>; <id_imgn>...]
```

### Rejoindre la page d'une enchère :
```
clt : JNAUC <id_enchere>

srv : JNAUC <nb_participant> <titre> <description> <montant> <temps> <image> (vient de rejoindre)
srv : JNAUC <nb_participant> (participe déjà à l'enchère)
srv : ERROR 33 // Id_enchere incorrect
srv : ERROR 40 // Déjà présent sur une enchère
```

### Participant quitte l'enchère :
```
clt : LVAUC

srv : LVAUC <nb_participant>
srv : ERROR 41 // Présent sur aucune enchère
```


