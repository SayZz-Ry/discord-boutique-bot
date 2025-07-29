# Boutique Discord pour Bessans
> Bot Discord permettant de gérer une petite boutique de produits (T-shirts, casquettes, mugs, etc.) et d'acquérir des articles via un **bouton PayPal**.

## 🚀 Installation

1. Cloner ce dépôt.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Copier le fichier d'exemple d'environnement et renseigner vos clés :
   ```bash
   cp dot.env .env
   ```
   - `DISCORD_TOKEN` : votre token du bot Discord.
   - `PAYPAL_USER` : nom d'utilisateur PayPal (ex. `MonComptePayPal`).
4. Lancer le bot :
   ```bash
   python bot_boutique.py
   ```

## 🔧 Configuration

Toutes les variables de configuration se trouvent dans le fichier `.env` :
```dotenv
DISCORD_TOKEN=...
PAYPAL_USER=...
```

## ➕ Ajouter le bot à votre serveur

Pour inviter le bot dans votre serveur Discord :

1. Rendez-vous sur le portail des développeurs Discord : https://discord.com/developers/applications
2. Sélectionnez votre application correspondant à ce bot.
3. Dans le menu de gauche, cliquez sur **OAuth2 > URL Generator**.
4. Dans **Scopes**, cochez **bot** et **applications.commands**.
5. Dans la section **Bot Permissions**, sélectionnez les permissions nécessaires (par exemple : Envoyer des messages, Gérer les messages, Intégrer des liens).
6. Copiez l’URL générée, collez-la dans votre navigateur et choisissez le serveur où inviter le bot.

## 📝 Commandes disponibles

| Commande                   | Description                                                      | Permissions    |
|----------------------------|------------------------------------------------------------------|----------------|
| `/produits`                | Liste les produits disponibles                                   | Tout le monde  |
| `/acheter <id> <quantité>` | Crée une commande et affiche un **bouton PayPal** pour le paiement | Tout le monde  |
| `/mes_commandes`           | Affiche l'historique de vos commandes                            | Tout le monde  |
| `/stock <id>`              | Affiche le stock disponible pour un produit                      | Tout le monde  |
| `/ajouter_produit ...`     | Ajoute un produit à la base (nom, description, prix, stock)      | Administrateur |
| `/supprimer_produit <id>`  | Supprime un produit si aucune commande n'existe pour celui-ci     | Administrateur |
| `/liste_produits_admin`    | Liste tous les produits avec leurs IDs                           | Administrateur |
| `/toutes_commandes`        | Affiche toutes les commandes enregistrées                        | Administrateur |
| `/annuler_commande ...`    | Annule une commande par produit et date                          | Administrateur |
| `/modifier_statut <commande_id> <statut>` | Modifie le statut d'une commande                           | Administrateur |

## 🛠️ Fonctionnement interne

- Base de données SQLite (`boutique.db`) générée automatiquement au démarrage.
- Table `produits` pour les articles, `commandes` pour le suivi des achats.
