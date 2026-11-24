import {
  Manrope_400Regular,
  Manrope_500Medium,
  Manrope_600SemiBold,
  Manrope_700Bold,
  Manrope_800ExtraBold,
  useFonts,
} from '@expo-google-fonts/manrope';
import { PlayfairDisplay_600SemiBold } from '@expo-google-fonts/playfair-display';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';

import { AuthProvider, useAuth } from '@/auth/auth-context';
import { colors, fonts } from '@/components/theme';

// Keep the splash screen up until we know whether someone is signed in.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    Manrope_400Regular,
    Manrope_500Medium,
    Manrope_600SemiBold,
    Manrope_700Bold,
    Manrope_800ExtraBold,
    PlayfairDisplay_600SemiBold,
  });
  // Keep the splash screen until the fonts are ready (or failed — then system fonts are used).
  if (!fontsLoaded && !fontError) return null;

  return (
    <AuthProvider>
      <SplashScreenController />
      <StatusBar style="dark" />
      <RootNavigator />
    </AuthProvider>
  );
}

function SplashScreenController() {
  const { ready } = useAuth();
  if (ready) SplashScreen.hide();
  return null;
}

/**
 * Which screens exist depends on the state:
 * not signed in -> login / register; signed in but no couple -> create or join one;
 * in a couple -> the main tabs. When the state changes, Expo Router moves
 * to an allowed screen by itself.
 */
function RootNavigator() {
  const { ready, user, couple, startError, onboarding } = useAuth();
  // Until we know who is signed in, show nothing (the splash screen is still up),
  // otherwise the guards below would briefly redirect away from the opened screen.
  if (!ready) return null;
  const online = !startError;
  const signedIn = online && !!user;
  const aboutYou = signedIn && onboarding;
  const inCouple = signedIn && !onboarding && !!couple;
  const needsCouple = signedIn && !onboarding && !couple;

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        headerStyle: { backgroundColor: colors.background },
        headerTintColor: colors.text,
        headerTitleStyle: { color: colors.text, fontFamily: fonts.bold, fontSize: 17 },
        headerShadowVisible: false,
        headerBackButtonDisplayMode: 'minimal',
      }}>
      <Stack.Protected guard={!online}>
        <Stack.Screen name="offline" />
      </Stack.Protected>

      <Stack.Protected guard={online && !signedIn}>
        <Stack.Screen name="login" />
        <Stack.Screen name="register" />
      </Stack.Protected>

      <Stack.Protected guard={aboutYou}>
        <Stack.Screen name="onboarding" />
      </Stack.Protected>

      <Stack.Protected guard={needsCouple}>
        <Stack.Screen name="couple" />
      </Stack.Protected>

      <Stack.Protected guard={inCouple}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="new-idea" options={modal('Новая идея')} />
        <Stack.Screen name="suggest" options={page('Подкинь идею')} />
        <Stack.Screen name="task" options={modal('План')} />
        <Stack.Screen name="wish" options={modal('Желание')} />
        <Stack.Screen name="gift-note" options={modal('Секретная заметка')} />
        <Stack.Screen name="gift-notes" options={page('Секретные заметки')} />
        <Stack.Screen name="my-wishlist" options={page('Мой вишлист')} />
        <Stack.Screen name="me" options={page('')} />
        <Stack.Screen name="account" options={page('Аккаунт')} />
        <Stack.Screen name="gift-suggest" options={page('Что подарить?')} />
        <Stack.Screen name="memory-form" options={modal('Воспоминание')} />
        <Stack.Screen name="memory/[id]" options={page('')} />
        <Stack.Screen name="profile" options={page('Мой профиль')} />
        <Stack.Screen name="partner" options={page('Партнёр')} />
        <Stack.Screen name="couple-edit" options={modal('Наша пара')} />
        <Stack.Screen name="test/[id]" options={page('Тест')} />
        <Stack.Screen name="test-result" options={page('Результат')} />
        <Stack.Screen name="notifications" options={page('Уведомления')} />
        <Stack.Screen name="notification-settings" options={page('Настройки уведомлений')} />
      </Stack.Protected>
    </Stack>
  );
}

function page(title: string) {
  return { headerShown: true, title };
}

function modal(title: string) {
  return { headerShown: true, title, presentation: 'modal' as const };
}
