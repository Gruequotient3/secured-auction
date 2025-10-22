# Plateforme de vente / achat par enchères

Dépot d'un projet de développement d'une platformes d'enchère (plus ou moins) sécurisée.

## Fonctionnalité requise

1. Mise en place d’une application serveur qui gère la mise aux enchères de plusieurs objets.
    - Initialisation d’une mise en vente aux enchères ”publique” d’un objet : les informations transmises du
service vers les acheteurs doivent être authentifiées, et peuvent être chiffrées.
    - Récupération des différentes propositions des acheteurs pour un objet donné : elles devront être chiffrées, authentifiées et associées à l’objet en vente. Puis, mise à jour et transmission du prix de vente aux
acheteurs.
    - Important : on souhaite que les acheteurs ne puissent pas connaître l’actuel leader de la mise aux enchères.
    - Il y a aura un intervalle de temps durant lequel l’enchère sera disponible. Par ailleurs, l’enchère doit être
supérieure au prix. La validité d’une proposition d’enchère devra donc être vérifiée (mettre en place un
protocole pour cela).
    - Proclamation publique et authentifiée du résultat, ainsi que du nom de l’acquéreur (qui ne devra pas être
publié/accessible avant).
2. Mise en place d’une application client qui permet aux acheteurs de se renseigner sur les différents objets mis
en vente, et de proposer des ”promesses d’achat”.
    - Transmission d’une proposition d’achat chiffrée et authentifiée.
    - Actualisation du prix de vente, en vérifiant bien l’authenticité de cette mise à jour.
    - Pareil pour la réception du résultat.
Le client disposera d’une interface graphique ”agréable d’utilisation”.
3. Mise en place d’une application client malhonnête, qui illustre qu’un participant malhonnête (par exemple,
un participant n’ayant pas la bonne clé), ne peut pas briser la sécurité des (ou de certaines) fonctionnalités
listées ci-dessus.

## Fonctionnalité optionnel

Pistes d’amélioration. Voici quelques suggestions d’amélioration. Attention, elles peuvent demander plus ou moins de travail de refactoring suivant la manière dont vous avez réalisé votre implantation initiale.

1. Créer une fonctionnalité côté client, qui permet de proposer une mise aux enchères (”client vendeur”).
2. Possibilité pour un acheteur de se rétracter pendant un petit intervalle de temps (disons, 10 secondes).
3. Associer à chaque client une valeur de cagnotte qu’il peut créditer (directement, ou via le résultat d’un mise
aux enchères, voir (a)), ou débiter pour une proposition d’achat.