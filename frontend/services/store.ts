/**
 * Redux Store configuration for PneumoVision AI.
 * Manages global state for authentication, predictions, and UI.
 */

import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Types
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  profile_image?: string;
  created_at: string;
}

interface Prediction {
  id: string;
  prediction: string;
  confidence: number;
  probability_normal: number;
  probability_pneumonia: number;
  image_path: string;
  gradcam_image?: string;
  report_pdf?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface UIState {
  darkMode: boolean;
  sidebarOpen: boolean;
  isUploading: boolean;
  isAnalyzing: boolean;
}

interface PredictionState {
  history: Prediction[];
  currentPrediction: Prediction | null;
  stats: any;
  total: number;
  page: number;
}

// Auth Slice
const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    isLoading: true,
  } as AuthState,
  reducers: {
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
      state.isAuthenticated = action.payload !== null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});

// UI Slice
const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    darkMode: false,
    sidebarOpen: false,
    isUploading: false,
    isAnalyzing: false,
  } as UIState,
  reducers: {
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
    },
    setDarkMode: (state, action: PayloadAction<boolean>) => {
      state.darkMode = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setUploading: (state, action: PayloadAction<boolean>) => {
      state.isUploading = action.payload;
    },
    setAnalyzing: (state, action: PayloadAction<boolean>) => {
      state.isAnalyzing = action.payload;
    },
  },
});

// Prediction Slice
const predictionSlice = createSlice({
  name: 'predictions',
  initialState: {
    history: [],
    currentPrediction: null,
    stats: null,
    total: 0,
    page: 1,
  } as PredictionState,
  reducers: {
    setHistory: (state, action: PayloadAction<{ predictions: Prediction[]; total: number }>) => {
      state.history = action.payload.predictions;
      state.total = action.payload.total;
    },
    setCurrentPrediction: (state, action: PayloadAction<Prediction | null>) => {
      state.currentPrediction = action.payload;
    },
    setStats: (state, action: PayloadAction<any>) => {
      state.stats = action.payload;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    addPrediction: (state, action: PayloadAction<Prediction>) => {
      state.history.unshift(action.payload);
      state.currentPrediction = action.payload;
    },
    removePrediction: (state, action: PayloadAction<string>) => {
      state.history = state.history.filter((p) => p.id !== action.payload);
    },
  },
});

// Export actions
export const {
  setUser,
  setLoading: setAuthLoading,
  logout,
} = authSlice.actions;

export const {
  toggleDarkMode,
  setDarkMode,
  toggleSidebar,
  setSidebarOpen,
  setUploading,
  setAnalyzing,
} = uiSlice.actions;

export const {
  setHistory,
  setCurrentPrediction,
  setStats,
  setPage,
  addPrediction,
  removePrediction,
} = predictionSlice.actions;

// Configure store
export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    ui: uiSlice.reducer,
    predictions: predictionSlice.reducer,
  },
  devTools: process.env.NODE_ENV !== 'production',
});

// Types for dispatch and selector
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

