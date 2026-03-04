# Manuel Utilisateur EMS

## 1. Introduction
L’Enquiry Management System (EMS) est une application métier qui gère tout le cycle commercial des demandes clients dans un contexte d’export/trading pharmaceutique.

EMS permet aux équipes de travailler dans un système unique, au lieu d’utiliser des feuilles Excel et des chaînes d’e-mails.

Utilisateurs typiques :
- Business Development (BD)
- Utilisateurs Admin
- Utilisateurs Super Admin
- Utilisateurs Supply Chain

Avec EMS, les utilisateurs peuvent :
- enregistrer et suivre les enquiries
- préparer des quotations et des révisions
- gérer les décisions d’approbation
- créer des enregistrements de Purchase Orders
- créer des factures et enregistrer les paiements
- suivre les livraisons
- consulter les KPI et exporter des rapports

## 2. Démarrage
### 2.1 Création de compte utilisateur
À ce stade, les comptes sont créés par un administrateur système.

1. Demandez un accès à votre administrateur EMS.
2. Fournissez votre nom, votre e-mail et le rôle requis (BD/Admin/SuperAdmin/Supply Chain).
3. Attendez la confirmation d’activation du compte.

Note : l’interface ne propose pas d’inscription autonome.

### 2.2 Connexion
1. Ouvrez l’URL EMS fournie par votre équipe.
2. Sur la page **Login**, saisissez :
   - **Username**
   - **Password**
3. Cliquez sur **Sign in**.
4. Si la connexion réussit, vous arrivez sur le Dashboard.

Si un avertissement de connectivité API apparaît, cliquez sur **Retry API Check** puis réessayez.

### 2.3 Réinitialisation du mot de passe
La réinitialisation autonome n’est pas encore disponible dans l’interface.

En cas d’oubli de mot de passe :
1. Contactez votre administrateur EMS.
2. Demandez une réinitialisation.
3. Reconnectez-vous avec le nouveau mot de passe.

## 3. Navigation dans l’interface
Après connexion, EMS utilise une mise en page standard :

- **Menu latéral gauche** (desktop) : modules principaux
- **En-tête supérieur** : titre de page, fil d’Ariane, utilisateur courant, logout
- **Zone centrale** : listes, formulaires, actions, détails

Sections principales :
- **Dashboard**
- **Customers**
- **Manufacturers**
- **Products**
- **Imports** (Admin/SuperAdmin)
- **Enquiries**
- **Commercial**
- **Reports** (Admin/SuperAdmin)

Conseils de navigation :
1. Cliquez sur un module dans le menu.
2. Dans les listes, cliquez sur une ligne pour charger le détail/l’édition.
3. Utilisez les boutons **Back** dans les écrans de détail.
4. Surveillez les notifications (toast) en haut à droite.

## 4. Gestion des données de référence (Master Data)
Les données de référence incluent Customers, Manufacturers et Products.

### 4.1 Customers
1. Ouvrez **Customers**.
2. Dans **Create Customer**, renseignez :
   - Code
   - Name
   - Country
   - Contact Email/Phone (optionnel)
   - case Active
3. Cliquez sur **Create**.
4. Pour modifier, cliquez sur une ligne du tableau.
5. Mettez à jour les champs dans **Customer Details** puis cliquez sur **Update**.
6. Pour désactiver, décochez **Active** puis enregistrez.

### 4.2 Manufacturers
1. Ouvrez **Manufacturers**.
2. Dans **Create Manufacturer**, renseignez code, name, country, Active.
3. Cliquez sur **Create**.
4. Sélectionnez une ligne pour modifier.
5. Cliquez sur **Update** pour enregistrer.
6. Pour désactiver, décochez **Active** puis enregistrez.

### 4.3 Products
1. Ouvrez **Products**.
2. Dans **Create Product**, renseignez :
   - SKU
   - Name
   - Manufacturer
   - Unit
   - Active
3. Cliquez sur **Create**.
4. Sélectionnez un produit pour modifier son détail.
5. Cliquez sur **Update** pour enregistrer.
6. Pour désactiver, décochez **Active** puis enregistrez.

### 4.4 Import Excel (si votre rôle le permet)
1. Ouvrez **Imports**.
2. Choisissez **Master Type** : Customers / Manufacturers / Products.
3. Importez un fichier Excel/CSV.
4. Cliquez sur **Upload and Process**.
5. Vérifiez le résumé :
   - Rows
   - Created
   - Updated
   - Errors
6. En cas d’erreurs, corrigez le fichier source et relancez l’import.

## 5. Gestion des enquiries
### 5.1 Créer une nouvelle enquiry
1. Ouvrez **Enquiries**.
2. Cliquez sur **Create Enquiry**.
3. Renseignez l’en-tête :
   - Customer
   - Received Date
   - Currency
   - Notes (optionnel)
4. Ajoutez une ou plusieurs lignes :
   - Product
   - Quantity
   - Target Price (optionnel)
   - Notes (optionnel)
5. Cliquez sur **Create Enquiry**.

### 5.2 Suivre les enquiries
Dans la liste **Enquiries**, utilisez les filtres :
- Status
- Customer
- Date from / date to

Cliquez sur le numéro d’enquiry pour ouvrir le détail.

### 5.3 Voir l’historique
Dans **Enquiry Details** :
- **Status History** affiche la chronologie des transitions.
- **Enquiry Items** affiche les lignes demandées.
- **Transition Status** permet (selon rôle) de faire avancer le statut avec commentaire.

## 6. Création des quotations
### 6.1 Créer une quotation depuis une enquiry
1. Ouvrez une enquiry dans **Enquiry Details**.
2. Cliquez sur **Create Quotation**.
3. EMS ouvre la page quotation correspondante.

### 6.2 Créer une révision de quotation
1. Dans **Create Revision**, renseignez :
   - Freight
   - Markup %
   - Currency
2. Ajoutez/modifiez les lignes :
   - Product
   - Qty
   - Unit Price
   - Linked enquiry item (optionnel)
   - Notes (optionnel)
3. Cliquez sur **Create Revision**.

### 6.3 Comprendre les totaux
Pour chaque révision, EMS affiche :
- Subtotal (somme des lignes)
- Freight
- Total final (incluant la marge)

Vous pouvez changer de révision via le sélecteur de révision.

## 7. Workflow d’approbation
### 7.1 Soumettre à approbation
1. Ouvrez la révision à valider.
2. Dans **Approval Actions**, cliquez sur **Submit Revision**.

### 7.2 Approuver ou rejeter
Les approbateurs autorisés (Admin/SuperAdmin) peuvent :
1. Saisir un commentaire dans la zone de texte.
2. Cliquer sur **Approve** ou **Reject**.

Important :
- Le commentaire est obligatoire pour approve/reject.
- La **Approval Timeline** enregistre décisions et remarques.

## 8. Purchase Orders
Les actions PO deviennent disponibles après approbation d’une révision.

### 8.1 Customer PO
1. Sur la page quotation, allez dans **Create Customer PO / RTM PO**.
2. Renseignez les champs optionnels (PO No, date, montant, statut).
3. Cliquez sur **Create Customer PO**.

### 8.2 RTM PO
1. Dans la même section, complétez le formulaire RTM PO.
2. Sélectionnez un fabricant si nécessaire.
3. Cliquez sur **Create RTM PO**.

Lien entre PO et quotation :
- Les deux types de PO sont liés à la révision approuvée.
- Ils servent de contexte commercial pour la facturation et l’exécution.

## 9. Suivi des factures et paiements
Utilisez la page **Commercial**.

### 9.1 Créer une facture
1. Dans **Create Invoice**, sélectionnez l’enquiry.
2. Liez éventuellement un Customer PO.
3. Renseignez dates, devise et montant (si nécessaire).
4. Cliquez sur **Create Invoice**.

### 9.2 Enregistrer un paiement
1. Dans **Add Payment**, sélectionnez la facture.
2. Saisissez date de paiement, montant, méthode, référence, notes.
3. Cliquez sur **Add Payment**.

### 9.3 Prévention du surpaiement
Si le montant dépasse le total de la facture :
- EMS bloque l’opération.
- Un message d’erreur s’affiche.
- Saisissez un montant valide et recommencez.

### 9.4 Suivi de livraison
1. Dans **Create Delivery**, saisissez les informations d’expédition.
2. Cliquez sur **Create Delivery**.
3. Dans **Add Delivery Event**, ajoutez des événements (ex. `IN_TRANSIT`, `DELIVERED`).

## 10. Reporting
Ouvrez **Reports** (Admin/SuperAdmin).

### 10.1 Consulter les KPI
1. Définissez des filtres optionnels :
   - Date from
   - Date to
   - Status
2. Cliquez sur **Refresh KPIs**.

Blocs KPI disponibles :
- Approval Rate
- PO Conversion
- Collected / Outstanding
- Delivery Completion

### 10.2 Exporter les rapports Excel
Utilisez les boutons **Excel Export** pour télécharger :
- `enquiries.xlsx`
- `quotations.xlsx`
- `invoices.xlsx`
- `payments.xlsx`

## 11. Rôles et permissions
### Business Development (BD)
Actions typiques :
- créer et suivre les enquiries
- travailler sur quotations/révisions
- piloter le flux enquiry
- coordonner les étapes orientées client

### Admin
Actions typiques :
- toutes les actions opérationnelles BD
- approbations (avec SuperAdmin)
- imports et contrôle commercial élargi

### Super Admin
Actions typiques :
- supervision globale
- décisions d’approbation critiques
- accès complet au reporting

### Supply Chain
Actions typiques :
- support d’exécution commerciale
- participation aux RTM PO
- opérations de suivi logistique

Note : les menus et actions visibles dépendent automatiquement du rôle.

## 12. Cas d’usage complet
Exemple de cycle complet :

1. Créer les référentiels customer, manufacturer et product.
2. Créer une enquiry avec lignes produit.
3. Ouvrir le détail enquiry et créer une quotation.
4. Créer une révision avec prix, freight et markup.
5. Soumettre la révision pour approbation.
6. L’approbateur valide avec commentaire.
7. Créer un Customer PO et/ou un RTM PO.
8. Aller dans Commercial et créer la facture.
9. Enregistrer le(s) paiement(s) client.
10. Créer la livraison et ajouter les événements de suivi.
11. Ouvrir Reports et exporter les KPI/Excel.

## 13. Dépannage
### Problème : connexion impossible
- Vérifiez username/password.
- Vérifiez que votre compte est actif.
- Si un avertissement API apparaît, cliquez sur **Retry API Check**.
- Contactez l’administrateur si le problème continue.

### Problème : données absentes dans les listes
- Supprimez les filtres (status/customer/date).
- Rafraîchissez la page.
- Vérifiez que votre rôle autorise l’accès au module.

### Problème : échec d’approbation
- Vérifiez que la révision a d’abord été soumise.
- Ajoutez un commentaire obligatoire avant approve/reject.
- Vérifiez que votre rôle est autorisé à approuver.

### Problème : erreurs de validation formulaire
- Renseignez tous les champs obligatoires.
- Respectez les formats (date, numérique, longueur du code devise).
- Corrigez les champs signalés puis soumettez à nouveau.

### Problème : paiement refusé
- Comparez le total de facture et le montant du paiement.
- Réduisez le montant pour éviter le surpaiement.

## 14. Bonnes pratiques
1. Gardez des référentiels propres (pas de doublons, nommage cohérent).
2. Renseignez des commentaires utiles lors des transitions et approbations.
3. Utilisez les révisions plutôt que d’écraser les hypothèses tarifaires.
4. Utilisez les filtres date/customer/status pour cibler les priorités.
5. Exportez régulièrement les rapports pour les revues métier.
6. Désactivez les données obsolètes au lieu de créer des quasi-doublons.
7. Utilisez les raccourcis du Dashboard pour aller plus vite.
8. Pour les démos/formations, Admin/SuperAdmin peuvent utiliser **DEMO DATA**.
