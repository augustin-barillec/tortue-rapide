# Tortue rapide

Ce repository rassemble notre code et documentation pour Franklin.

## Franklin cli
Cette magnifique CLI permet d'automatiser les process longs et chiants de l'utilisation de Franklin.  
À l'heure actuelle il ne fait qu'entraîner un model à partir d'un tub, soit sur le pi, soit local. Ce n'est pas encore très poussé donc si vous déviez du script, tout va péter !  
(Refacto pour plus de propreté et de confort à venir un jour)

### Prérequis
* Python3
* Être connecté sur le réseau prévu à cet effet, celui qui fait le pont entre votre machine et le Pi
* Mettre en place la machine tensorflow-gpu, sur laquelle l'entraînement de Franklin aura lieu
  * Se procurer les droits sur la machine (Gorbinator pourra vous assister, s'il grogne donnez lui du chocoloat)
  * Se créer un environnement virtuel python3 et installer donkey_car 
  ```
    #ssh into the instance
    apt-get install python3-venv
    python3 -m venv env
    source env/bin/activate
    pip install wheel
    pip install donkeycar==2.5.1
    pip install tensorflow-gpu==1.8.0
    donkey createcar --template donkey2 ~/mycar
    ```

## Franklin base configuration

### Steering values :
key|value
---|---
*LEFT* | 480
*RIGHT* | 310

### Throttling Values :
key | values
---|---
*FORWARD* | 390 (400 for race)
*STOP* | 360
*REWIND* | 330
