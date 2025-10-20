import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Import de votre module d'émotion personnalisé
try:
    from emotion_layer import EmotionEngine, DecisionMaker
    CUSTOM_ENGINE_AVAILABLE = True
except ImportError:
    st.warning("⚠️ Module emotion_layer.py non trouvé - utilisation de l'IA standard")
    CUSTOM_ENGINE_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Smart Plant AI Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé amélioré
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2e8b57;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #2e8b57, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .hybrid-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    .rules-card {
        background: linear-gradient(135deg, #4caf50, #2e8b57);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .comparison-table th, .comparison-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    .comparison-table th {
        background-color: #f0f8f4;
    }
    .match {
        background-color: #e8f5e8;
    }
    .mismatch {
        background-color: #ffe8e8;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header"> Surveillance et Émotions des Plantes</h1>', unsafe_allow_html=True)

# =============================================================================
# MODULE IA HYBRIDE - COMBINAISON IA ML + RÈGLES MÉTIER
# =============================================================================

class HybridPlantAI:
    def __init__(self):
        self.ml_model = None
        self.rules_engine = None
        self.decision_maker = None
        self.is_trained = False
        
        if CUSTOM_ENGINE_AVAILABLE:
            self.rules_engine = EmotionEngine()
            self.decision_maker = DecisionMaker()
    
    def generate_training_data(self, n_samples=1000):
        """Génère des données d'entraînement réalistes pour l'IA"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Génération de données réalistes
            temp = np.random.normal(24, 4)
            humidity = np.random.normal(60, 15)
            light = np.random.normal(800, 300)
            
            # Utilisation des règles métier si disponible, sinon règles de base
            if self.rules_engine:
                sensor_data = {
                    "temperature": temp,
                    "humidity": humidity, 
                    "lightLevel": light,
                    "soilMoisture": np.random.normal(50, 20)  # Simulation humidité sol
                }
                emotion = self.rules_engine.computeEmotion(sensor_data)
                # Conversion des émotions texte en format standard
                if "happy" in emotion.lower():
                    emotion = "happy"
                elif "sad" in emotion.lower():
                    emotion = "sad"
                elif "tired" in emotion.lower() or "sleepy" in emotion.lower():
                    emotion = "tired"
                else:
                    emotion = "happy"  # défaut
            else:
                # Règles de base
                if (20 <= temp <= 28) and (45 <= humidity <= 75) and (500 <= light <= 1200):
                    emotion = 'happy'
                elif (temp < 18 or temp > 30) or (humidity < 30 or humidity > 85) or (light < 300 or light > 1500):
                    emotion = 'sad'
                else:
                    emotion = 'tired'
            
            data.append({
                'temperature': max(10, min(40, temp)),
                'humidity': max(10, min(95, humidity)),
                'lightLevel': max(100, min(2000, light)),
                'emotion': emotion
            })
        
        return pd.DataFrame(data)
    
    def train_ml_model(self):
        """Entraîne le modèle de machine learning"""
        training_data = self.generate_training_data(2000)
        
        X = training_data[['temperature', 'humidity', 'lightLevel']]
        y = training_data['emotion']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.ml_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.ml_model.fit(X_train, y_train)
        
        y_pred = self.ml_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        self.is_trained = True
        
        joblib.dump(self.ml_model, 'hybrid_plant_ai_model.pkl')
        
        return training_data, accuracy
    
    def load_ml_model(self):
        """Charge le modèle ML"""
        try:
            self.ml_model = joblib.load('hybrid_plant_ai_model.pkl')
            self.is_trained = True
            return True
        except:
            return False
    
    def predict_ml(self, temperature, humidity, light):
        """Prédiction par Machine Learning"""
        if not self.is_trained:
            return "non_entraine", 0, {}
        
        features = np.array([[temperature, humidity, light]])
        prediction = self.ml_model.predict(features)[0]
        probabilities = self.ml_model.predict_proba(features)[0]
        
        prob_dict = dict(zip(self.ml_model.classes_, probabilities))
        return prediction, max(probabilities), prob_dict
    
    def predict_rules(self, temperature, humidity, light):
        """Prédiction par règles métier"""
        if not self.rules_engine:
            return "rules_unavailable", 0, {}
        
        sensor_data = {
            "temperature": temperature,
            "humidity": humidity,
            "lightLevel": light,
            "soilMoisture": 50  # Valeur par défaut pour la démo
        }
        
        emotion = self.rules_engine.computeEmotion(sensor_data)
        happiness = self.rules_engine.evaluateHappiness(light, temperature)
        thirst = self.rules_engine.evaluateThirst(50)  # Valeur par défaut
        
        # Conversion en probabilités simulées
        if "happy" in emotion.lower():
            probs = {"happy": 0.8, "sad": 0.1, "tired": 0.1}
        elif "sad" in emotion.lower():
            probs = {"happy": 0.1, "sad": 0.8, "tired": 0.1}
        else:
            probs = {"happy": 0.1, "sad": 0.1, "tired": 0.8}
        
        return emotion, happiness/100, probs
    
    def hybrid_predict(self, temperature, humidity, light):
        """Prédiction hybride combinant ML et règles"""
        ml_pred, ml_conf, ml_probs = self.predict_ml(temperature, humidity, light)
        rules_pred, rules_conf, rules_probs = self.predict_rules(temperature, humidity, light)
        
        # Combinaison des résultats (poids: 70% ML, 30% règles)
        if ml_pred != "non_entraine" and rules_pred != "rules_unavailable":
            final_probs = {}
            for emotion in ['happy', 'sad', 'tired']:
                ml_prob = ml_probs.get(emotion, 0)
                rules_prob = rules_probs.get(emotion, 0)
                final_probs[emotion] = 0.7 * ml_prob + 0.3 * rules_prob
            
            final_emotion = max(final_probs, key=final_probs.get)
            final_confidence = final_probs[final_emotion]
            
            return {
                "final_emotion": final_emotion,
                "final_confidence": final_confidence,
                "final_probs": final_probs,
                "ml_emotion": ml_pred,
                "ml_confidence": ml_conf,
                "rules_emotion": rules_pred,
                "rules_confidence": rules_conf,
                "method": "hybrid"
            }
        elif ml_pred != "non_entraine":
            return {
                "final_emotion": ml_pred,
                "final_confidence": ml_conf,
                "final_probs": ml_probs,
                "ml_emotion": ml_pred,
                "ml_confidence": ml_conf,
                "rules_emotion": "N/A",
                "rules_confidence": 0,
                "method": "ml_only"
            }
        else:
            return {
                "final_emotion": rules_pred,
                "final_confidence": rules_conf,
                "final_probs": rules_probs,
                "ml_emotion": "N/A",
                "ml_confidence": 0,
                "rules_emotion": rules_pred,
                "rules_confidence": rules_conf,
                "method": "rules_only"
            }

# Initialisation de l'IA hybride
hybrid_ai = HybridPlantAI()

# =============================================================================
# INTERFACE STREAMLIT
# =============================================================================

# Sidebar
with st.sidebar:
    st.header(" Configuration IA Hybride")
    
    # Mode de prédiction
    prediction_mode = st.radio(
        "🎯 Mode de prédiction:",
        ["Hybride (ML + Règles)", "Machine Learning uniquement", "Règles métier uniquement"],
        index=0
    )
    
    st.markdown("---")
    
    # Chargement des modèles
    if st.button(" Charger modèle IA hybride"):
        if hybrid_ai.load_ml_model():
            st.success("✅ Modèle IA hybride chargé!")
        else:
            st.warning("⚠️ Nouveau modèle nécessaire")
    
    if st.button(" Entraîner nouveau modèle"):
        with st.spinner("Entraînement du modèle hybride..."):
            data, accuracy = hybrid_ai.train_ml_model()
            st.success(f"✅ Modèle entraîné! Précision: {accuracy:.2%}")
    
    st.markdown("---")
    
    # Statut des modules
    st.subheader("📊 Statut des modules")
    st.write(f"Machine Learning: {'✅ Actif' if hybrid_ai.is_trained else '❌ Inactif'}")
    st.write(f"📋 Règles métier: {'✅ Actif' if CUSTOM_ENGINE_AVAILABLE else '❌ Inactif'}")
    if CUSTOM_ENGINE_AVAILABLE:
        st.write(f"🎯 Moteur de décision: {'✅ Actif' if hybrid_ai.decision_maker else '❌ Inactif'}")

# Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs(["🔮 Prédictions", "📊 Comparaison", "🎯 Règles Métier", "🌿 Dashboard"])

with tab1:
    st.header("🔮 Prédictions Intelligentes")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(" Paramètres d'entrée")
        
        temperature = st.slider("🌡️ Température (°C)", 10.0, 40.0, 22.0, 0.5)
        humidity = st.slider("💧 Humidité (%)", 10.0, 95.0, 60.0, 1.0)
        light = st.slider("☀️ Lumière (lux)", 100, 2000, 800, 50)
        
        # Paramètres avancés pour les règles
        if CUSTOM_ENGINE_AVAILABLE:
            st.subheader("🌱 Paramètres sol (règles)")
            soil_moisture = st.slider("💦 Humidité du sol (%)", 0.0, 100.0, 50.0, 1.0)
        
        if st.button(" Lancer l'analyse hybride", type="primary"):
            with st.spinner("Analyse en cours par le système hybride..."):
                # Prédiction selon le mode sélectionné
                if prediction_mode == "Hybride (ML + Règles)":
                    result = hybrid_ai.hybrid_predict(temperature, humidity, light)
                elif prediction_mode == "Machine Learning uniquement":
                    ml_pred, ml_conf, ml_probs = hybrid_ai.predict_ml(temperature, humidity, light)
                    result = {
                        "final_emotion": ml_pred,
                        "final_confidence": ml_conf,
                        "final_probs": ml_probs,
                        "method": "ml_only"
                    }
                else:  # Règles métier uniquement
                    rules_pred, rules_conf, rules_probs = hybrid_ai.predict_rules(temperature, humidity, light)
                    result = {
                        "final_emotion": rules_pred,
                        "final_confidence": rules_conf,
                        "final_probs": rules_probs,
                        "method": "rules_only"
                    }
                
                # Affichage des résultats
                with col2:
                    emotion_emoji = {"happy": "😊", "sad": "😢", "tired": "🥵"}.get(
                        result["final_emotion"].lower() if 'happy' in result["final_emotion"].lower() else 
                        'sad' if 'sad' in result["final_emotion"].lower() else
                        'tired', "❓"
                    )
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                                padding: 2rem; border-radius: 15px; color: white; text-align: center;">
                        <h2>{emotion_emoji} {result['final_emotion']}</h2>
                        <h3>Confiance: {result['final_confidence']:.2%}</h3>
                        <p>Méthode: {result['method']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Graphique des probabilités
                    if result["final_probs"]:
                        fig_proba = px.bar(
                            x=list(result["final_probs"].keys()),
                            y=list(result["final_probs"].values()),
                            title="Probabilités de prédiction",
                            color=list(result["final_probs"].keys()),
                            color_discrete_map={
                                'happy': '#4caf50',
                                'sad': '#ff6b6b',
                                'tired': '#ffb74d'
                            }
                        )
                        fig_proba.update_layout(yaxis_tickformat='.0%')
                        st.plotly_chart(fig_proba, use_container_width=True)
                    
                    # Détails des différentes méthodes
                    with st.expander("🔍 Détails des différentes méthodes"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if "ml_emotion" in result and result["ml_emotion"] != "N/A":
                                st.write("**🤖 Machine Learning:**")
                                st.write(f"- Émotion: {result['ml_emotion']}")
                                st.write(f"- Confiance: {result['ml_confidence']:.2%}")
                        
                        with col_b:
                            if "rules_emotion" in result and result["rules_emotion"] != "N/A":
                                st.write("**📋 Règles métier:**")
                                st.write(f"- Émotion: {result['rules_emotion']}")
                                st.write(f"- Confiance: {result['rules_confidence']:.2%}")

with tab2:
    st.header("📊 Comparaison des Méthodes")
    
    if not hybrid_ai.is_trained or not CUSTOM_ENGINE_AVAILABLE:
        st.warning("Les deux modules (ML et Règles) doivent être disponibles pour la comparaison")
    else:
        # Génération de données de test
        st.subheader("🧪 Test de comparaison")
        
        test_cases = [
            {"temp": 22, "humidity": 65, "light": 800, "description": "Conditions optimales"},
            {"temp": 35, "humidity": 40, "light": 1200, "description": "Trop chaud"},
            {"temp": 18, "humidity": 85, "light": 200, "description": "Froid et sombre"},
            {"temp": 28, "humidity": 25, "light": 600, "description": "Air sec"}
        ]
        
        comparison_data = []
        for case in test_cases:
            ml_pred, ml_conf, ml_probs = hybrid_ai.predict_ml(case["temp"], case["humidity"], case["light"])
            rules_pred, rules_conf, rules_probs = hybrid_ai.predict_rules(case["temp"], case["humidity"], case["light"])
            
            comparison_data.append({
                "Description": case["description"],
                "Température": case["temp"],
                "Humidité": case["humidity"],
                "Lumière": case["light"],
                "ML_Émotion": ml_pred,
                "ML_Confiance": f"{ml_conf:.2%}",
                "Règles_Émotion": rules_pred,
                "Règles_Confiance": f"{rules_conf:.2%}",
                "Concordance": "✅" if ml_pred in rules_pred.lower() else "❌"
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
        
        # Statistiques de concordance
        matches = sum(1 for row in comparison_data if row["Concordance"] == "✅")
        total = len(comparison_data)
        concordance_rate = matches / total
        
        st.metric("📈 Taux de concordance", f"{concordance_rate:.2%}")

with tab3:
    st.header("🎯 Règles Métier - EmotionEngine")
    
    if not CUSTOM_ENGINE_AVAILABLE:
        st.error("Module emotion_layer.py non disponible")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Règles implémentées")
            
            st.markdown("""
            <div class="rules-card">
            <h4>🌊 Règles d'humidité du sol:</h4>
            <ul>
            <li>Sol sec (&lt;30%) → 😢 Triste (assoiffée)</li>
            <li>Sol trop humide (&gt;80%) → 💧 Mouillée (trop d'eau)</li>
            <li>Sol optimal (30-80%) → ✅ Bonne hydratation</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="rules-card">
            <h4>🌡️ Règles de température:</h4>
            <ul>
            <li>Très chaud (&gt;35°C) → 🥵 Fatiguée (trop chaud)</li>
            <li>Température optimale (20-30°C) → ✅ Confortable</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="rules-card">
            <h4>☀️ Règles de lumière:</h4>
            <ul>
            <li>Lumière faible (&lt;300 lux) → 😴 Endormie</li>
            <li>Lumière optimale (400-800 lux) → ✅ Éveillée</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("🧮 Calculateurs")
            
            # Calculateur de bonheur
            st.write("**😊 Calculateur de bonheur:**")
            col_a, col_b = st.columns(2)
            with col_a:
                happiness_light = st.slider("Lumière (lux)", 0, 2000, 800, key="happiness_light")
            with col_b:
                happiness_temp = st.slider("Température (°C)", 10, 40, 25, key="happiness_temp")
            
            happiness_score = hybrid_ai.rules_engine.evaluateHappiness(happiness_light, happiness_temp)
            st.progress(happiness_score/100)
            st.write(f"Score de bonheur: {happiness_score}%")
            
            # Calculateur de soif
            st.write("**💧 Calculateur de soif:**")
            soil_moisture = st.slider("Humidité du sol (%)", 0, 100, 50, key="thirst_moisture")
            thirst_score = hybrid_ai.rules_engine.evaluateThirst(soil_moisture)
            st.progress(thirst_score/100)
            st.write(f"Niveau de soif: {thirst_score}%")
            
            # Test du DecisionMaker
            st.write("**🤖 Test du DecisionMaker:**")
            test_data = {
                "soilMoisture": soil_moisture,
                "temperature": happiness_temp,
                "lightLevel": happiness_light
            }
            
            should_water = hybrid_ai.decision_maker.shouldWaterPlant(test_data)
            is_optimal = hybrid_ai.decision_maker.isEnvironmentOptimal(test_data)
            
            st.write(f"💧 Arrosage nécessaire: {'✅ Oui' if should_water else '❌ Non'}")
            st.write(f"🌿 Environnement optimal: {'✅ Oui' if is_optimal else '❌ Non'}")

with tab4:
    st.header("🌿 Dashboard Hybride")
    
    # Lecture des données réelles
    try:
        with open("results/output_results.json", "r", encoding="utf-8") as f:
            plants = json.load(f)
    except FileNotFoundError:
        st.error("Fichier JSON introuvable !")
        plants = []
    
    if plants:
        # Analyse hybride des données
        analysis_data = []
        for plant in plants:
            if hybrid_ai.is_trained and CUSTOM_ENGINE_AVAILABLE:
                result = hybrid_ai.hybrid_predict(
                    plant['temperature'], 
                    plant['humidity'], 
                    plant['lightLevel']
                )
                plant['hybrid_emotion'] = result['final_emotion']
                plant['confidence'] = result['final_confidence']
                plant['method'] = result['method']
            elif hybrid_ai.is_trained:
                pred, conf, _ = hybrid_ai.predict_ml(
                    plant['temperature'], 
                    plant['humidity'], 
                    plant['lightLevel']
                )
                plant['hybrid_emotion'] = pred
                plant['confidence'] = conf
                plant['method'] = 'ml_only'
            elif CUSTOM_ENGINE_AVAILABLE:
                pred, conf, _ = hybrid_ai.predict_rules(
                    plant['temperature'], 
                    plant['humidity'], 
                    plant['lightLevel']
                )
                plant['hybrid_emotion'] = pred
                plant['confidence'] = conf
                plant['method'] = 'rules_only'
            
            analysis_data.append(plant)
        
        df = pd.DataFrame(analysis_data)
        
        # KPI
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_plants = len(df)
            st.metric("Plantes totales", total_plants)
        
        with col2:
            happy_plants = len(df[df['hybrid_emotion'].str.contains('happy', case=False, na=False)])
            st.metric("Plantes heureuses", f"{happy_plants}/{total_plants}")
        
        with col3:
            avg_confidence = df['confidence'].mean()
            st.metric("Confiance moyenne", f"{avg_confidence:.2%}")
        
        with col4:
            methods_used = df['method'].value_counts()
            main_method = methods_used.index[0] if len(methods_used) > 0 else "N/A"
            st.metric("Méthode principale", main_method)
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Émotions (Hybride)")
            emotion_counts = df['hybrid_emotion'].value_counts()
            fig_emotion = px.pie(
                values=emotion_counts.values,
                names=emotion_counts.index,
                title="Distribution des émotions - Analyse hybride"
            )
            st.plotly_chart(fig_emotion, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Méthodes utilisées")
            method_counts = df['method'].value_counts()
            fig_method = px.bar(
                x=method_counts.index,
                y=method_counts.values,
                title="Répartition des méthodes d'analyse"
            )
            st.plotly_chart(fig_method, use_container_width=True)
        
        # Tableau détaillé
        st.subheader("📋 Données détaillées avec analyse hybride")
        display_cols = ['deviceId', 'temperature', 'humidity', 'lightLevel', 'hybrid_emotion', 'confidence', 'method']
        st.dataframe(df[display_cols], use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🧠 Smart Plant AI Hybrid • IA Machine Learning + Règles Métier • " + 
    datetime.now().strftime("%Y-%m-%d %H:%M") +
    "</div>", 
    unsafe_allow_html=True
)