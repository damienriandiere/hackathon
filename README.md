# Emotion Race

![Logo du Projet](Logo.png)

## Description

**Emotion Race** est un projet innovant qui combine la technologie des capteurs physiologiques (**EDA et ECG**) avec un jeu interactif pour adapter dynamiquement la difficulté en fonction de l'état émotionnel du joueur.  

Les capteurs **EDA** et **ECG** mesurent respectivement la conductance de la peau et la fréquence cardiaque, permettant de détecter le stress mental.  

L'interface du jeu, développée en **Python** avec la librairie **PyGame**, présente un personnage qui doit éviter des obstacles sous forme de balles.  
👉 Lorsque le stress est détecté, **l'écran devient flou**, rendant la visibilité plus difficile et augmentant ainsi la difficulté du jeu.

### 🎯 Objectif principal  
Créer une **expérience de jeu immersive et adaptative** où le joueur peut apprendre à gérer son stress pour améliorer ses performances.  
En adaptant la difficulté du jeu en temps réel en fonction des réactions physiologiques du joueur, **Emotion Race** vise à sensibiliser les utilisateurs à la gestion du stress et à leur fournir un **outil ludique** pour s'entraîner à rester calme sous pression

## 📖 Table des Matières

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Fonctionnalités](#fonctionnalités)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Auteurs](#auteurs)

## Installation

1. **Installer le projet en local** :

```bash
git clone https://github.com/damienriandiere/EmotionRace.git
cd EmotionRace
pip install -r requirements.txt
```

2. **Installer les capteurs physiologiques comme sur les photos ci-dessous** :  
   - 📍 **Capteur EDA** : [Positionnement capteurs EDA](Positionnement_EDA.png)
   - 📍 **Capteur ECG** : [Positionnement capteurs ECG](Positionnement_ECG.png)

## Utilisation
Une fois le projet installé et les capteurs positionnés, suivez ces étapes pour l'utilissation : 

1. **Lancez la collecte des données physiologiques** :  
   ```bash
   python sensors/stress_detection.py
   ```

2. ⏳ **Attendre que la calibration se fasse** : 
   La calibration prend 20 secondes. Pendant ce temps, restez calme et immobile.

3. **Lancez le jeu** : 
   ```bash
   python -m game.main.py
   ```

## Fonctionnalités  

### 🎮 Mécaniques de jeu  
✔️ Contrôle d'un ninja qui doit éviter des balles.  
✔️ **Lorsque le stress est détecté, l'écran devient flou**, rendant le jeu plus difficile.  
✔️ Interface fluide et immersive développée avec **PyGame**.  

### 📡 Adaptation en fonction du stress  
✔️ Intégration de capteurs **EDA (conductance de la peau)** et **ECG (fréquence cardiaque)**.  
✔️ Calibration automatique des capteurs au début du jeu (20 secondes).  
✔️ Analyse en temps réel du stress pour modifier la visibilité à l'écran.  

### 📊 Système de feedback  
✔️ **Indicateur visuel** du niveau de stress en cours de partie.  
✔️ **Leaderboard** affiché à la fin du jeu pour comparer les performances des joueurs.  

### 🔧 Personnalisation  
✔️ Possibilité d’ajuster certains paramètres du jeu (*sensibilité au stress, effet de flou*).  
✔️ Possibilité de jouer sans les capteurs.  

## Contribuer

Les contributions sont les bienvenues ! Veuillez suivre les étapes suivantes pour contribuer :

1. **Forkez** le dépôt.
2. **Créez une branche** pour votre fonctionnalité :  
   ```bash
   git checkout -b feature/ma-fonctionnalité
    ```
3. **Committez** vos modifications :
   ```bash
   git commit -am 'Ajout de ma fonctionnalité'
   ```
4. **Pushez** votre branche :
   ```bash
    git push origin feature/ma-fonctionnalité
    ```
5. **Ouvrez** une Pull Request.

## Licence

Ce projet est sous licence **Apache 2.0**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteurs
Ce projet a été réalisé par :  

- **[Tomm JOBIT](https://github.com/tjobit)**
- **[Axel DEFO MBOBDA](https://github.com/axeldefo)**
- **[Damien RIANDIERE](https://github.com/damienriandiere)** 

💡 Nous avons tous contribué de manière équivalente au développement du projet. 🚀  
