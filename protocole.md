# Plateforme de vente / achat par enchères

## Environnement

### Langages/outils:
Serveur : Python - Bottle, Flask, FastAPI (indécidé)

Client : HTML/CSS/JS

Base de données : SQL

## Sécurité

### Informations chiffrées
- Proposition de vente
- Pseudo
- Gagnant

### Informations non chiffrées
- Informations des objets à vendre
- Dernière enchère
- Temps restant

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

