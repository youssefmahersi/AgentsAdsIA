# 06 · Brancher Meta Ads pour que l'agent mette tes pubs en ligne

Une fois ce connecteur branché, tu dis « mets les pubs du dossier livraisons/… dans l'ensemble X » et l'agent fait tout le travail :
- il envoie les vidéos et les images ;
- il crée les créas avec le texte, le titre, le bouton et le lien ;
- il crée les pubs **en pause**.

**C'est toi qui actives.**

## 1. Brancher le connecteur officiel Meta
Dans le terminal :
```bash
claude mcp add --transport http meta-ads https://mcp.facebook.com/ads
```
Puis lance Claude Code dans ton dossier (`cd ~/AgentsAds && claude`) et tape :
```
/mcp
```
Choisis **meta-ads** puis **Authenticate**. Une page Facebook s'ouvre : connecte-toi avec le compte qui gère tes comptes publicitaires et accepte les accès (comptes pub, pages, Instagram).

Vérifie avec :
```
Liste mes comptes publicitaires Meta et leurs pages.
```

## 2. Préparer le compte (une seule fois, par toi)
- **Partager le pixel avec le compte pub**, dans le Business Manager → Sources de données → ton pixel → Comptes publicitaires. Sans ça, Meta refuse de créer les pubs (erreur 1815045).
- **Vérifier le domaine de la boutique** dans Business Manager → Sécurité de la marque → Domaines.
- **Relier la page Facebook (et Instagram)** au compte pub.

## 3. La répartition des rôles (important)
| Qui | Fait quoi |
|---|---|
| **Toi** | Créer la **campagne** et les **ensembles de publicités** : objectif, budget, pays, audience, emplacements. Ce sont des décisions d'argent. |
| **L'agent** | Créer les **pubs** dans tes ensembles : envoyer les fichiers, poser le texte, le titre, le bouton et le lien, nommer selon la naming convention, en pause. |
| **Toi** | Relire les pubs dans le Gestionnaire, puis **activer**. |

Les agents n'activent jamais une pub et ne changent jamais un budget.

## 4. Ce que tu donnes à l'agent
```
Mets en ligne les pubs de livraisons/2026-11-02/<produit>/ dans le compte <nom du compte>, campagne <nom>, ensemble <nom>.
Page : <nom de la page>. Lien : <URL de la page produit ou de l'advertorial>. Bouton : Shop Now.
Textes : le fichier TEXTE-META.md de chaque dossier. Nomme chaque pub selon 08-NAMING.md. Tout en pause.
```

## 5. Ce que l'agent respecte (déjà dans ses consignes)
- **Pubs créées en PAUSE**, jamais activées.
- **Aucune case « contenu généré par IA » cochée** : c'est toi qui décides, à la main, dans le Gestionnaire.
- **Images** : déposées par le connecteur (envoi local puis finalisation), et la vignette des vidéos passe par l'image extraite.
- **Vidéos de plus de 100 Mo** : réencodées avant l'envoi (H.264, 9:16, son AAC).
- **Un seul fichier par pub.** Chaque hook (H1, H2, H3) est une pub séparée.
- **Lien** : vers la bonne page (produit, advertorial ou listicle) selon l'étape TOFU, MOFU ou BOFU. L'agent vérifie que la page répond avant de créer la pub.
- **Après création** : l'agent relit le statut de chaque pub. « En cours d'examen » est normal. En cas de refus, il te le signale et ne publie rien d'autre à la place.

## 6. Pubs refusées : quoi faire
Meta ne donne pas toujours le motif par l'API. Lis-le dans le Gestionnaire ou dans « Qualité du compte ». Puis demande :
```
omar, cette pub a été refusée pour <motif>. Fais un audit de conformité et propose la version corrigée sans perdre le punch.
```

Les causes les plus fréquentes :
- un attribut personnel (« your » + maladie, âge ou religion) ;
- un avant / après sur le corps ;
- une fausse urgence ;
- un faux média.

**Ne modifie pas une pub active** pour la corriger : la modification la renvoie en examen et relance l'apprentissage. Crée plutôt la version corrigée comme nouvelle pub, puis coupe l'ancienne.
