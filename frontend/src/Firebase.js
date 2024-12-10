// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC2--EfWfKcQBb4qwpR_LjpC3SrDHrknuU",
  authDomain: "ai-ml-chatbot.firebaseapp.com",
  projectId: "ai-ml-chatbot",
  storageBucket: "ai-ml-chatbot.firebasestorage.app",
  messagingSenderId: "1022278784649",
  appId: "1:1022278784649:web:e09711bcc0d29cdb0bd858",
  measurementId: "G-V5LQ6P1GRY"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider, signInWithPopup };
