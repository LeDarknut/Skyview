# Skyview
Un module python permettant de générer une vue du ciel et de l'exporter au format vectoriel.

## Catalogues
Skyview inclut la possibilité de créer des catalogues au format utilisé par le module, depuis des fichiers CSV notamment, Convert.py
Les catalogues Bright et Hipparcos sont fournis.

## Interface
Afin de naviguer dans le ciel, Skyview propose une extension utilisant Pygame, Render.py
Une fois le script lancé, utilisez les touches :
flèches : se déplacer
c : tourner en sens horaire
v : tourner en sens anti-horaire
entrer : se rendre à un emplacement en coordonéées d'ascension droite et en déclinaison
espace : prendre une capture svg de la vue et l'enregistrer dans le dossier shot

## Remarque
Il est ensuite nécessaire d'utiliser un logiciel tiers pour effectuer le rendu svg
