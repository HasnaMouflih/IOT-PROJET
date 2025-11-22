import { initializeApp } from "firebase/app";
import { getDatabase, ref, onValue } from "firebase/database";

const firebaseConfig = {
  apiKey: "AIzaSyAFo8XdOcymTCLZSqQUvG-csZNN3AzSQ7E",
  authDomain: "smart-plant-free.firebaseapp.com",
  databaseURL: "https://smart-plant-free-default-rtdb.firebaseio.com",
  projectId: "smart-plant-free",
  storageBucket: "smart-plant-free.firebasestorage.app",
  messagingSenderId: "955457614635",
  appId: "1:955457614635:web:293f501931e0917c2fcb6e"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

// ✅ Ajout de l'export de app
export { app, db, ref, onValue };
