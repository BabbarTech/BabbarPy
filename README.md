# BabbarPy

Ce projet consiste en l'utilisation de fichiers Python exécutables en ligne de commande (CLI) pour interagir avec l'API de babbar.tech. L'objectif est d'extraire des métriques en utilisant l'outil fourni sur des listes d'URLs, de hosts ou de couples d'URLs.

## Prérequis

Avant d'exécuter les scripts Python, assurez-vous d'avoir les éléments suivants :

1. Python installé sur votre système (version 3.11.3 ou supérieure).
2. Les bibliothèques Python requises. Vous pouvez les installer en exécutant la commande suivante (faire tourner `setup.py` permet de s'en assurer) :
   pip install -r requirements.txt

## Configuration

Avant de pouvoir utiliser les scripts, vous devez fournir certaines informations de configuration. Voici les étapes à suivre :

1. Lancez le fichier `setup.py`.
2. Il vous sera demandé de fournir votre clé API dans le terminal.

Alternative : créez un fichier config.ini :

```
[API]
api_key: VOTRE_CLÉ_API
```

Remplacez `VOTRE_CLÉ_API` par votre clé d'API fournie par babbar.tech.

## Utilisation

Pour exécuter les scripts et obtenir des métriques à partir de différentes listes, suivez les instructions ci-dessous :

1. Ouvrez une invite de commande dans le répertoire du projet.
2. Exécutez les scripts Pythons correspondant à vos besoins `nom_de_la_fonction.py` avec les arguments appropriés. Voici quelques exemples :

   - Pour exploiter une liste d'URLs contenue dans un fichier texte :
     ```
     python url_backlinks_url.py urls.txt
     ```

   - Pour exploiter une liste de hosts :
     ```
     python host_health.py hosts.txt
     ```

   - Pour exploiter une liste de couples d'URLs : (n'oubliez pas de placer les sources en 1e colonne et les target en 2e colonne)
     ```
     python url_fi.py couples.csv
     ```

   Assurez-vous d'adapter les noms de fichiers et les types en fonction de vos besoins.
   
## Autres cas d'utilisation prévus
   
   Pour exploiter les scripts comme une bibliothèque python, les fonctions de base sont accessibles à l'import python
   
   (`from BabbarPY.host import *` est maintenant possible)

## Ressources supplémentaires

- Documentation de l'API de babbar.tech : [lien vers la documentation](https://www.babbar.tech/doc-api/)
- Problèmes connus : consultez le fichier `issues.md`, lorsqu'il est présent, pour une liste des problèmes connus et des solutions de contournement.
