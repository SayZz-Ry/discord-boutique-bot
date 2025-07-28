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

## 🛠️ Fonctionnement interne

- Base de données SQLite (`boutique.db`) générée automatiquement au démarrage.
- Table `produits` pour les articles, `commandes` pour le suivi des achats.
