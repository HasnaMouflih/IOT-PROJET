import { db } from "../firebase";
import { ref, onValue } from "firebase/database";
import { useEffect } from "react";

export default function FirebaseTest() {
  useEffect(() => {
    const testRef = ref(db, "/");

    onValue(testRef, (snap) => {
      console.log("🔥 Connected to Firebase, root data:", snap.val());
    });
  }, []);

  return null;
}
