import discord
from discord import app_commands
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PAYPAL_USER = os.getenv('PAYPAL_USER', 'toncompte')

DATABASE_FILE = 'boutique.db'
DATE_FORMAT = "%d/%m/%Y"



def initialiser_base_donnees():
    """Initialise la base de données SQLite avec les tables nécessaires"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Création de la table des produits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            description TEXT NOT NULL,
            prix REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Création de la table des commandes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            total REAL NOT NULL,
            statut TEXT DEFAULT 'en_attente',
            date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits (id)
        )
    ''')
    
    # Insertion des produits par défaut s'ils n'existent pas
    cursor.execute('SELECT COUNT(*) FROM produits')
    if cursor.fetchone()[0] == 0:
        produits_defaut = [
            ("T-shirt Bessans", "T-shirt en coton avec le logo de Bessans", 25.0, 50),
            ("Casquette Montagne", "Casquette de randonnée avec protection UV", 15.0, 30),
            ("Mug Bessans", "Mug en céramique avec vue sur les montagnes", 12.0, 25),
            ("Poster Panoramique", "Poster A3 des plus belles vues de Bessans", 8.0, 40),
            ("Stickers Pack", "Pack de 5 stickers Bessans pour voiture", 5.0, 100)
        ]
        cursor.executemany('''
            INSERT INTO produits (nom, description, prix, stock)
            VALUES (?, ?, ?, ?)
        ''', produits_defaut)
    
    conn.commit()
    conn.close()

def ajouter_commande(user_id, produit_id, quantite, prix_unitaire):
    """Ajoute une nouvelle commande à la base de données"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    total = quantite * prix_unitaire
    
    cursor.execute('''
        INSERT INTO commandes (user_id, produit_id, quantite, prix_unitaire, total)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, produit_id, quantite, prix_unitaire, total))
    
    # Mise à jour du stock
    cursor.execute('''
        UPDATE produits 
        SET stock = stock - ? 
        WHERE id = ?
    ''', (quantite, produit_id))
    
    conn.commit()
    conn.close()

def obtenir_commandes_utilisateur(user_id):
    """Récupère toutes les commandes d'un utilisateur"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.produit_id, c.quantite, c.prix_unitaire, c.total, c.statut, c.date_commande
        FROM commandes c
        WHERE c.user_id = ?
        ORDER BY c.date_commande DESC
    ''', (user_id,))
    
    commandes = []
    for row in cursor.fetchall():
        commandes.append({
            'user_id': user_id,
            'produit_id': row[0],
            'quantite': row[1],
            'prix_unitaire': row[2],
            'total': row[3],
            'statut': row[4],
            'date_commande': row[5]
        })
    
    conn.close()
    return commandes

def obtenir_toutes_commandes():
    """Récupère toutes les commandes"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, user_id, produit_id, quantite, prix_unitaire, total, statut, date_commande
        FROM commandes
        ORDER BY date_commande DESC
    ''')
    
    commandes = []
    for row in cursor.fetchall():
        commandes.append({
            'id': row[0],
            'user_id': row[1],
            'produit_id': row[2],
            'quantite': row[3],
            'prix_unitaire': row[4],
            'total': row[5],
            'statut': row[6],
            'date_commande': row[7]
        })
    
    conn.close()
    return commandes

def verifier_stock(produit_id, quantite):
    """Vérifie si un produit a assez de stock"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT stock FROM produits WHERE id = ?', (produit_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0] >= quantite:
        return True
    return False

def calculer_montant(produit, quantite):
    return quantite * produit['prix']

def generer_lien_paypal(produit, quantite, montant):
    note = f"{produit['nom']} x{quantite}".replace(' ', '+')
    return f"https://www.paypal.com/paypalme/{PAYPAL_USER}/{montant}?locale.x=fr_FR&note={note}"

def format_commandes(user_id, commandes):
    user_cmd = [c for c in commandes if c['user_id'] == user_id]
    if not user_cmd:
        return "Tu n'as aucune commande. 😢\nAchète vite des produits de la boutique !"
    
    produits = obtenir_produits()
    msg = "__**🛒 Tes commandes :**__\n"
    for c in user_cmd:
        produit = next((p for p in produits if p['id'] == c['produit_id']), None)
        if produit:
            msg += (
                f"📦 **{produit['nom']}**\n"
                f"   📊 Quantité : {c['quantite']}x\n"
                f"   💶 Prix unitaire : {c['prix_unitaire']} €\n"
                f"   💰 Total : {c['total']} €\n"
                f"   📋 Statut : {c['statut']}\n"
                "-----------------------------\n"
            )
    msg += "\nMerci pour tes achats ! 🛍️"
    return msg



def obtenir_produits():
    """Récupère tous les produits depuis la base de données"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nom, description, prix, stock FROM produits ORDER BY id')
    
    produits = []
    for row in cursor.fetchall():
        produits.append({
            'id': row[0],
            'nom': row[1],
            'description': row[2],
            'prix': row[3],
            'stock': row[4]
        })
    
    conn.close()
    return produits

def ajouter_produit(nom, description, prix, stock):
    """Ajoute un nouveau produit à la base de données"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO produits (nom, description, prix, stock)
        VALUES (?, ?, ?, ?)
    ''', (nom, description, prix, stock))
    
    produit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return produit_id

def supprimer_produit(produit_id):
    """Supprime un produit de la base de données"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nom FROM produits WHERE id = ?', (produit_id,))
    produit = cursor.fetchone()
    
    if not produit:
        conn.close()
        return False
    
    cursor.execute('SELECT COUNT(*) FROM commandes WHERE produit_id = ?', (produit_id,))
    nb_commandes = cursor.fetchone()[0]
    
    if nb_commandes > 0:
        conn.close()
        return False
    
    cursor.execute('DELETE FROM produits WHERE id = ?', (produit_id,))
    conn.commit()
    conn.close()
    
    return True

def logement_choices():
    """Retourne les choix de produits pour les commandes Discord"""
    produits = obtenir_produits()
    return [app_commands.Choice(name=p['nom'], value=p['id']) for p in produits]

def statut_choices():
    """Retourne les choix de statut pour les commandes Discord"""
    return [
        app_commands.Choice(name="En attente", value="en_attente"),
        app_commands.Choice(name="Payée", value="paye"),
        app_commands.Choice(name="Expédiée", value="envoye"),
        app_commands.Choice(name="Annulée", value="annule"),
    ]

def verifier_permissions_admin(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur a les permissions d'administrateur"""
    if not interaction.user.guild_permissions.administrator:
        return False
    return True

# Initialisation du bot
class MonClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MonClient()

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    # Initialisation de la base de données au démarrage
    initialiser_base_donnees()
    print("Base de données initialisée avec succès !")

@bot.tree.command(name="produits", description="Liste les produits disponibles")
async def produits(interaction: discord.Interaction):
    produits = obtenir_produits()
    msg = "__**🛍️ Produits disponibles dans la boutique :**__\n"
    for p in produits:
        msg += f"🆔 **{p['id']}** - **{p['nom']}** ({p['prix']} €)\n   {p['description']}\n   📦 Stock : {p['stock']} unités\n\n"
    await interaction.response.send_message(msg)

@bot.tree.command(name="ajouter_produit", description="Ajoute un nouveau produit (Admin)")
@app_commands.describe(
    nom="Nom du produit",
    description="Description du produit",
    prix="Prix en euros",
    stock="Quantité en stock"
)
async def ajouter_produit_cmd(interaction: discord.Interaction, nom: str, description: str, prix: float, stock: int):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return
    
    # Validation des données
    if prix <= 0:
        await interaction.response.send_message("❌ Le prix doit être positif.", ephemeral=True)
        return
    
    if stock < 0:
        await interaction.response.send_message("❌ Le stock ne peut pas être négatif.", ephemeral=True)
        return
    
    if len(nom) < 3:
        await interaction.response.send_message("❌ Le nom du produit doit contenir au moins 3 caractères.", ephemeral=True)
        return
    
    if len(description) < 10:
        await interaction.response.send_message("❌ La description doit contenir au moins 10 caractères.", ephemeral=True)
        return
    
    try:
        produit_id = ajouter_produit(nom, description, prix, stock)
        await interaction.response.send_message(
            f"✅ Nouveau produit ajouté avec succès !\n"
            f"🛍️ **{nom}**\n"
            f"📝 {description}\n"
            f"💶 {prix} €\n"
            f"📦 Stock : {stock} unités\n"
            f"🆔 ID: {produit_id}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Erreur lors de l'ajout du produit : {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="supprimer_produit", description="Supprime un produit (Admin)")
@app_commands.describe(
    produit_id="ID du produit à supprimer"
)
async def supprimer_produit_cmd(interaction: discord.Interaction, produit_id: int):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Vérification si le produit existe
    cursor.execute('SELECT nom FROM produits WHERE id = ?', (produit_id,))
    produit = cursor.fetchone()
    
    if not produit:
        await interaction.response.send_message("❌ Produit introuvable.", ephemeral=True)
        conn.close()
        return
    
    # Vérification s'il y a des commandes pour ce produit
    cursor.execute('SELECT COUNT(*) FROM commandes WHERE produit_id = ?', (produit_id,))
    nb_commandes = cursor.fetchone()[0]
    
    if nb_commandes > 0:
        await interaction.response.send_message(
            f"❌ Impossible de supprimer ce produit car il a {nb_commandes} commande(s) active(s).",
            ephemeral=True
        )
        conn.close()
        return
    
    # Suppression du produit
    cursor.execute('DELETE FROM produits WHERE id = ?', (produit_id,))
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(
        f"✅ Produit **{produit[0]}** supprimé avec succès !",
        ephemeral=True
    )

@bot.tree.command(name="liste_produits_admin", description="Liste tous les produits avec leurs IDs (Admin)")
async def liste_produits_admin(interaction: discord.Interaction):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return
    
    produits = obtenir_produits()
    
    if not produits:
        msg = "Aucun produit enregistré."
    else:
        msg = "__**🛍️ Liste des produits (Admin) :**__\n"
        for p in produits:
            msg += f"🆔 **{p['id']}** - **{p['nom']}** ({p['prix']} €)\n   {p['description']}\n   📦 Stock : {p['stock']}\n\n"
    
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="acheter", description="Achète un produit")
@app_commands.describe(
    produit_id="Choisis un produit",
    quantite="Quantité à acheter"
)
async def acheter(
    interaction: discord.Interaction,
    produit_id: int,
    quantite: int
):
    produits = obtenir_produits()
    produit = next((p for p in produits if p['id'] == produit_id), None)
    if not produit:
        await interaction.response.send_message("Produit introuvable.", ephemeral=True)
        return
    
    if quantite <= 0:
        await interaction.response.send_message("❌ La quantité doit être positive.", ephemeral=True)
        return
    
    if not verifier_stock(produit_id, quantite):
        await interaction.response.send_message(
            f"❌ Stock insuffisant. Il ne reste que {produit['stock']} unité(s) en stock.",
            ephemeral=True
        )
        return
    
    montant = calculer_montant(produit, quantite)
    paypal_url = generer_lien_paypal(produit, quantite, montant)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Payer avec PayPal", url=paypal_url, style=discord.ButtonStyle.link))
    
    # Ajout de la commande en base de données
    ajouter_commande(interaction.user.id, produit['id'], quantite, produit['prix'])
    
    await interaction.response.send_message(
        f"Commande confirmée pour {produit['nom']} x{quantite} (\u20ac{montant}).\nMerci de procéder au paiement :",
        view=view
    )

@bot.tree.command(name="mes_commandes", description="Affiche tes commandes")
async def mes_commandes(interaction: discord.Interaction):
    commandes = obtenir_commandes_utilisateur(interaction.user.id)
    msg = format_commandes(interaction.user.id, commandes)
    await interaction.response.send_message(msg, ephemeral=True)



@bot.tree.command(name="stock", description="Affiche le stock d'un produit")
@app_commands.describe(
    produit_id="Choisis un produit pour voir son stock"
)
async def stock(interaction: discord.Interaction, produit_id: int):
    produits = obtenir_produits()
    produit = next((p for p in produits if p['id'] == produit_id), None)
    if not produit:
        await interaction.response.send_message("Produit introuvable.", ephemeral=True)
        return
    
    msg = f"📦 **{produit['nom']}**\n"
    msg += f"🆔 ID: {produit['id']}\n"
    msg += f"💰 Prix: {produit['prix']} €\n"
    msg += f"📊 Stock disponible: {produit['stock']} unité(s)\n"
    
    if produit['stock'] == 0:
        msg += "❌ **Rupture de stock !**"
    elif produit['stock'] <= 5:
        msg += "⚠️ **Stock faible !**"
    else:
        msg += "✅ **En stock**"
    
    await interaction.response.send_message(msg)

@bot.tree.command(name="annuler_commande", description="Annule une de tes commandes")
@app_commands.describe(
    produit_id="Choisis le produit de la commande à annuler",
    date_commande="Date de la commande à annuler (JJ/MM/AAAA)"
)
async def annuler_commande(interaction: discord.Interaction, produit_id: int, date_commande: str):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return
    
    # Vérification du format de date
    try:
        datetime.strptime(date_commande, DATE_FORMAT)
    except ValueError:
        await interaction.response.send_message(
            "❌ Format de date invalide. Utilise JJ/MM/AAAA.\n"
            "Exemple : 01/08/2025",
            ephemeral=True
        )
        return
    
    # Suppression de la commande
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM commandes
        WHERE user_id = ? AND produit_id = ? AND date_commande LIKE ?
    ''', (interaction.user.id, produit_id, f"{date_commande}%"))
    
    if cursor.rowcount > 0:
        conn.commit()
        produits = obtenir_produits()
        produit = next((p for p in produits if p['id'] == produit_id), None)
        await interaction.response.send_message(
            f"✅ Commande annulée avec succès pour {produit['nom']} du {date_commande}.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ Aucune commande trouvée avec ces critères.",
            ephemeral=True
        )
    
    conn.close()

@bot.tree.command(name="toutes_commandes", description="Affiche toutes les commandes (Admin)")
async def toutes_commandes(interaction: discord.Interaction):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return
    
    commandes = obtenir_toutes_commandes()
    
    if not commandes:
        msg = "Aucune commande enregistrée."
    else:
        msg = "__**📊 Toutes les commandes :**__\n"
        for c in commandes:
            produits = obtenir_produits()
            produit = next((p for p in produits if p['id'] == c['produit_id']), None)
            if produit:
                print(c)
                msg += f"🛍️ [ID:{c['id']}] **{produit['nom']}** - {c['quantite']}x ({c['total']} €) - User: {c['user_id']} - {c['statut']}\n"
    
    await interaction.response.send_message(msg, ephemeral=True)


@bot.tree.command(name="modifier_statut", description="Modifie le statut d'une commande (Admin)")
@app_commands.describe(
    commande_id="ID de la commande à modifier",
    statut="Nouveau statut de la commande"
)
@app_commands.choices(statut=statut_choices())
async def modifier_statut(interaction: discord.Interaction, commande_id: int, statut: app_commands.Choice[str]):
    # Vérification des permissions admin
    if not verifier_permissions_admin(interaction):
        await interaction.response.send_message("❌ Cette commande est réservée aux administrateurs.", ephemeral=True)
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE commandes SET statut = ? WHERE id = ?",
        (statut.value, commande_id)
    )
    if cursor.rowcount > 0:
        conn.commit()
        await interaction.response.send_message(
            f"✅ Statut de la commande {commande_id} mis à jour en **{statut.value}**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ Aucune commande trouvée avec cet ID.",
            ephemeral=True
        )
    conn.close()

if __name__ == "__main__":
    bot.run(TOKEN) 
