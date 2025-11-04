// Firebase 설정
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA1EOQ_bGUCltJ2o-FG6Ffxf7uwaipi0Nw",
  authDomain: "ddalkkak-a4842.firebaseapp.com",
  databaseURL: "https://ddalkkak-a4842-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "ddalkkak-a4842",
  storageBucket: "ddalkkak-a4842.firebasestorage.app",
  messagingSenderId: "245637066609",
  appId: "1:245637066609:web:802e03483622cc712b10d0",
  measurementId: "G-XDKXLJKM5F"
};

// Firebase 초기화
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);
const auth = getAuth(app);

export { db, auth, analytics };