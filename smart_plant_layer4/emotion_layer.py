# =============================================
# LAYER 4 - INTELLIGENCE & EMOTIONAL ENGINE
# =============================================
# Auteur : Aicha Hasni
# Description : Module IA pour analyser l'état émotionnel des plantes

class EmotionEngine:
    """
    Analyse les données capteurs et détermine l'émotion de la plante.
    """
    def __init__(self):
        # Règles simples que tu peux adapter plus tard
        self.emotionRules = {
            "dry_soil": lambda d: d.get("soilMoisture", 0) < 30,
            "overwatered": lambda d: d.get("soilMoisture", 0) > 80,
            "hot_temp": lambda d: d.get("temperature", 0) > 35,
            "low_light": lambda d: d.get("lightLevel", 0) < 300
        }

    def computeEmotion(self, sensorData: dict) -> str:
        """
        Retourne une émotion selon les valeurs des capteurs.
        """
        soil = sensorData.get("soilMoisture", 0)
        temp = sensorData.get("temperature", 0)
        light = sensorData.get("lightLevel", 0)

        # Ordre de priorité : soif > trop d’eau > chaleur > lumière faible > heureux
        if soil < 30:
            return "sad 😢 (assoiffée)"
        if soil > 80:
            return "wet 💧 (trop d'eau)"
        if temp > 35:
            return "tired 🥵 (trop chaud)"
        if light < 300:
            return "sleepy 😴 (pas assez de lumière)"
        return "happy 😊 (en bonne santé)"

    def evaluateHappiness(self, light: float, temp: float) -> int:
        """
        Calcule un score de bonheur (0-100) basé sur la lumière et la température.
        """
        light_score = max(0, min(light / 1000.0, 1.0))
        temp_score = max(0, 1.0 - abs(temp - 25.0) / 25.0)
        score = int(((light_score + temp_score) / 2) * 100)
        return max(0, min(score, 100))

    def evaluateThirst(self, soilMoisture: float) -> int:
        """
        Retourne un score de soif (0-100).
        """
        if soilMoisture > 80:
            return 0
        if soilMoisture > 50:
            return 30
        if soilMoisture > 30:
            return 60
        return 90


class DecisionMaker:
    """
    Prend des décisions automatiques selon l'état de la plante.
    """
    def __init__(self, autoMode: bool = True):
        self.autoMode = autoMode

    def shouldWaterPlant(self, sensorData: dict) -> bool:
        """
        Retourne True si la plante doit être arrosée.
        """
        return sensorData.get("soilMoisture", 0) < 40

    def isEnvironmentOptimal(self, sensorData: dict) -> bool:
        """
        Vérifie si l'environnement est idéal pour la plante.
        """
        soil = sensorData.get("soilMoisture", 0)
        temp = sensorData.get("temperature", 0)
        light = sensorData.get("lightLevel", 0)
        return (40 <= soil <= 80) and (20 <= temp <= 30) and (400 <= light <= 800)
