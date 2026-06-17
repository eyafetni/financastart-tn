
# f2_scoring/ahp_engine.py
import numpy as np

class AHPEngine:
    def __init__(self):
        # Valeur standard de Saaty pour l'indice aléatoire (Random Index) à n=4
        self.RANDOM_INDEX_4X4 = 0.90
        

    def compute_weights(self, matrix: np.ndarray) -> dict:
        """
        Exécute le calcul complet de l'AHP : normalisation, poids, 
        lambda_max et vérification du rapport de cohérence (CR).
        """
        n = matrix.shape[0]
        if n != 4:
            raise ValueError("Le moteur est configuré exclusivement pour des matrices 4x4.")

        # 1. Calcul du vecteur de priorité (Poids)
        column_sums = np.sum(matrix, axis=0)
        normalized_matrix = matrix / column_sums
        weights = np.mean(normalized_matrix, axis=1)

        # 2. Calcul de la cohérence mathématique
        weighted_vector = np.dot(matrix, weights)
        lambda_max = np.mean(weighted_vector / weights)
        
        # Indice de Cohérence (CI)
        ci = (lambda_max - n) / (n - 1)
        
        # Rapport de Cohérence (CR)
        cr = ci / self.RANDOM_INDEX_4X4

        return {
            "weights": weights,  # Retourne un array numpy pour les calculs suivants
            "consistency_ratio": round(cr, 4),
            "is_consistent": cr < 0.10  # Règle d'or de Saaty
        }

    def calculate_dimension_score(self, matrix: np.ndarray, sub_scores: list) -> tuple:
        """
        Prend la matrice Saaty d'une dimension et les 4 mini-scores de l'entrepreneur (0-100),
        puis retourne la note globale de la dimension (0-100) et son flag de cohérence.
        """
        ahp_data = self.compute_weights(matrix)
        weights = ahp_data["weights"]
        
        # Produit scalaire (Dot product) entre les poids et les scores de l'utilisateur
        final_score = np.dot(weights, sub_scores)
        
        return round(final_score, 1), ahp_data["is_consistent"], ahp_data["consistency_ratio"]

# ==========================================
# ZONE DE TEST (Pour valider ton code en J2)
# ==========================================
if __name__ == "__main__":
    engine = AHPEngine()

    matrice_green_test = np.array([
        [1.0,  0.33, 0.5,  0.5],   # Carbon
        [3.0,  1.0,  2.0,  2.0],   # Resources
        [2.0,  0.5,  1.0,  1.0],   # Biodiversity
        [2.0,  0.5,  1.0,  1.0]    # Pollution
    ])

    mini_scores_startup = [80, 20, 45, 30] 

    # Extraction des données intermédiaires pour vérification
    ahp_data = engine.compute_weights(matrice_green_test)
    score_final, valide, cr = engine.calculate_dimension_score(matrice_green_test, mini_scores_startup)
    
    print("=== RAPPORT DE SCORING INTERNE (MEMBRE 2) ===")
    print(f"Poids calculés par critère :")
    print(f"  - Carbon Footprint    : {ahp_data['weights'][0]*100:.2f}%")
    print(f"  - Resource Efficiency : {ahp_data['weights'][1]*100:.2f}%")
    print(f"  - Biodiversity Impact : {ahp_data['weights'][2]*100:.2f}%")
    print(f"  - Pollution Control   : {ahp_data['weights'][3]*100:.2f}%")
    print("-" * 45)
    print(f"Rapport de Cohérence (CR) : {cr * 100:.2f}%")
    print(f"Modèle mathématique valide ? : {'✅ Oui' if valide else '❌ Non'}")
    print("-" * 45)
    print(f"NOTE FINALE CALCULÉE : {score_final}/100")
    print("=============================================")