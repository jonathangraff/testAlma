Pour lancer le script : 

- cloner le repo Git : 

        git clone https://github.com/jonathangraff/testAlma.git

- aller dans le repo : 

        cd testAlma

- créer le container : 

        sudo docker build -t test_alma

- lancer le script :
    
        sudo docker run test_alma


Le programme est fait pour que toutes les "règles du jeu" soient inscrites dans le dictionnaire ***actions_dictionary*** de la ligne 82 du fichier **robot.py**.

Les différents paramètres sur lesquels on peut jouer sont dans les fonctions ***do_the_same_action*** et ***choose_new_action***. 

On y décide à quelle condition les robots gardent la même action que précédemment, et s'ils doivent changer, quelle sera leur nouvelle tâche.
