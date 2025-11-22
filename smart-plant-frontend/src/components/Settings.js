import React, { useState } from "react";
import { useAuth } from "./AuthContext";
import {
  getAuth,
  EmailAuthProvider,
  reauthenticateWithCredential,
  updatePassword,
  updateProfile,
} from "firebase/auth";
import "../style/settings.css"; 

const Settings = () => {
  const { currentUser } = useAuth();
  const auth = getAuth();

  const [displayName, setDisplayName] = useState(currentUser?.displayName || "");
  const [photoURL, setPhotoURL] = useState(currentUser?.photoURL || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");

  if (!currentUser) {
    return <p>Aucun utilisateur connecté.</p>;
  }

  const handleUpdateProfile = async () => {
    try {
      await updateProfile(currentUser, { displayName, photoURL });
      setMessage("Profil mis à jour !");
    } catch (error) {
      setMessage("Erreur : " + error.message);
    }
  };

  const handleChangePassword = async () => {
    try {
      const credential = EmailAuthProvider.credential(
        currentUser.email,
        currentPassword
      );
      await reauthenticateWithCredential(currentUser, credential);

      await updatePassword(currentUser, newPassword);
      setMessage("Mot de passe mis à jour !");

      setCurrentPassword("");
      setNewPassword("");
    } catch (error) {
      setMessage("Erreur : " + error.message);
    }
  };

  return (
    <div className="settings-page">
      <h2>Paramètres du compte</h2>

      {message && <div className="settings-message">{message}</div>}

      {/* Ligne des deux premières cartes côte à côte */}
      <div className="settings-cards-row">
        {/* Informations du compte */}
        <div className="settings-card">
          <h3>Informations du compte</h3>
          <p><strong>Email : </strong>{currentUser.email}</p>
          <p><strong>UID : </strong>{currentUser.uid}</p>
          <p><strong>Email vérifié : </strong>{currentUser.emailVerified ? "Oui" : "Non"}</p>
          <p><strong>Créé le : </strong>{new Date(currentUser.metadata.creationTime).toLocaleString()}</p>
          <p><strong>Dernière connexion : </strong>{new Date(currentUser.metadata.lastSignInTime).toLocaleString()}</p>
        </div>

        {/* Modifier le profil */}
        <div className="settings-card">
          <h3>Modifier le profil</h3>
          <label>Nom :</label>
          <input
            type="text"
            className="settings-input"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />

          <label>URL de la photo :</label>
          <input
            type="text"
            className="settings-input"
            value={photoURL}
            onChange={(e) => setPhotoURL(e.target.value)}
          />

          <button className="btn" onClick={handleUpdateProfile}>
            Sauvegarder le profil
          </button>
        </div>
      </div>

      {/* Carte mot de passe en dessous */}
      <div className="settings-card">
        <h3>Changer le mot de passe</h3>
        <label>Mot de passe actuel :</label>
        <input
          type="password"
          className="settings-input"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
        />

        <label>Nouveau mot de passe :</label>
        <input
          type="password"
          className="settings-input"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />

        <button className="btn-danger" onClick={handleChangePassword}>
          Mettre à jour le mot de passe
        </button>
      </div>
    </div>
  );
};

export default Settings;
