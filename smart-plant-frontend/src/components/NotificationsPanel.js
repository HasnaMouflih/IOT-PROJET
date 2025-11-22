import React, { useEffect, useState } from "react";
import { ref, onChildAdded, update } from "firebase/database";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import Slide from "@mui/material/Slide";
import { db } from "../firebase";

function NotificationsPanel({ plantId }) {
  const [open, setOpen] = useState(false);
  const [currentNotif, setCurrentNotif] = useState(null);

  useEffect(() => {
    if (!plantId) return;

    const notifRef = ref(db, `notifications/${plantId}`);

    const unsubscribe = onChildAdded(notifRef, (snapshot) => {
      const notif = snapshot.val();
      const key = snapshot.key;

      if (!notif.read) {
        setCurrentNotif(notif);
        setOpen(true);

        // Marquer la notif comme lue directement dans Firebase
        update(ref(db, `notifications/${plantId}/${key}`), { read: true });
      }
    });

    return () => unsubscribe();
  }, [plantId]);

  const handleClose = (_, reason) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  return (
    <Snackbar
      open={open}
      onClose={handleClose}
      autoHideDuration={4000}
      anchorOrigin={{ vertical: "top", horizontal: "center" }}
    >
      <Slide direction="down" in={open}>
        <Alert severity="info" variant="filled">
          {currentNotif?.message}
        </Alert>
      </Slide>
    </Snackbar>
  );
}

export default NotificationsPanel;
