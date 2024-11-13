pipeline {
    environment { 
        // Déclaration des variables d'environnement globales
        DOCKER_ID = "coliseerbx" // Remplacez par votre identifiant Docker
        DOCKER_IMAGE = "conges_app"
        DOCKER_TAG = "v.${BUILD_ID}.0" // Tag des images avec l'ID de build pour l'incrémentation automatique
    }
    agent any // Jenkins peut sélectionner n'importe quel agent disponible

    stages {
        stage('Docker Build') { 
            steps {
                script {
                    sh '''
                    docker rm -f conges || true
                    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                    sleep 6
                    '''
                }
            }
        }

        stage('Docker Run') { 
            steps {
                script {
                    sh '''
                    docker run -d -p 6000:6000 --name conges $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    sleep 10
                    '''
                }
            }
        }

        stage('Test Acceptance') { 
            steps {
                script {
                    sh '''
                    echo "Attente du démarrage de l'application sur localhost:6000..."
                    until curl -s localhost:6000 > /dev/null; do
                      echo "L'application n'est pas encore prête. Nouvelle tentative dans 5 secondes..."
                      sleep 5
                    done
                    # Vérification avec curl
                    curl localhost:6000
                    '''
                }
            }
        }

        stage('Docker Push') { 
            environment {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS") // Récupération du mot de passe Docker Hub depuis les credentials Jenkins
            }
            steps {
                script {
                    sh '''
                    docker login -u $DOCKER_ID -p $DOCKER_PASS
                    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        // Étape pour mettre à jour les fichiers YAML avant chaque déploiement
        stage('Update Kubernetes YAML Files') {
            steps {
                script {
                    // Mise à jour des fichiers YAML pour utiliser les nouveaux tags Docker
                    sh '''
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/deployment.yaml
                    '''
                }
            }
        }

        stage('Deploiement en dev') {
            environment {
                KUBECONFIG = credentials("config") // Récupération de kubeconfig depuis les credentials Jenkins
            }
            steps {
                script {
                    sh '''
                    kubectl apply -f kube/deployment.yaml -n dev
                    kubectl apply -f kube/hpa.yaml -n dev
                    kubectl apply -f kube/pv.yaml -n dev
                    kubectl apply -f kube/pvc.yaml -n dev
                    '''
                }
            }
        }

        stage('Deploiement en staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                    kubectl apply -f kube/deployment.yaml -n staging
                    kubectl apply -f kube/hpa.yaml -n staging
                    kubectl apply -f kube/pv.yaml -n staging
                    kubectl apply -f kube/pvc.yaml -n staging
                    '''
                }
            }
        }

        stage('Deploiement en prod') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    // Créer un bouton d'approbation avec un délai d'expiration de 15 minutes
                    def userInput = input(
                        id: 'userInput', message: 'Do you want to deploy in production?', ok: 'Yes',
                        parameters: [
                            choice(name: 'Approval', choices: ['Yes', 'No'], description: 'Select Yes to proceed')
                        ]
                    )

                    // Vérification de l'approbation de l'utilisateur pour le déploiement en production
                    if (userInput == 'Yes') {
                        echo "Déploiement en production approuvé, exécution du déploiement..."
                        sh '''
                        kubectl apply -f kube/deployment.yaml -n prod
                        kubectl apply -f kube/service.yaml -n prod
                        kubectl apply -f kube/ingress.yaml -n prod
                        kubectl apply -f kube/pv.yaml -n prod
                        kubectl apply -f kube/pvc.yaml -n prod
                        kubectl apply -f kube/hpa.yaml -n prod
                        '''
                    } else {
                        echo "Déploiement en production annulé par l'utilisateur."
                    }
                }
            }
        }
    }
}
