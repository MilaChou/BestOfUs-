import { Link } from 'expo-router';
import { useState } from 'react';
import { Text } from 'react-native';

import { useAuth } from '@/auth/auth-context';
import { colors } from '@/components/theme';
import { Button, ErrorText, Input, Screen, Subtitle, Title } from '@/components/ui';
import { ApiError, errorMessage } from '@/lib/api';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError('');
    setLoading(true);
    try {
      await signIn(email, password);
      // No navigation needed: once signed in, the root layout shows the next screen.
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 401
          ? 'Неверный email или пароль'
          : errorMessage(e),
      );
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Title>BestOfUs</Title>
      <Subtitle>Общее пространство для вас двоих</Subtitle>
      <Input
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        autoComplete="email"
        keyboardType="email-address"
        placeholder="you@example.com"
      />
      <Input
        label="Пароль"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        autoComplete="password"
        placeholder="Минимум 8 символов"
        onSubmitEditing={submit}
      />
      <ErrorText>{error}</ErrorText>
      <Button title="Войти" onPress={submit} loading={loading} disabled={!email || !password} />
      <Link href="/register" style={{ textAlign: 'center', padding: 8 }}>
        <Text style={{ color: colors.text, fontSize: 15 }}>
          Нет аккаунта? <Text style={{ fontWeight: '600', textDecorationLine: 'underline' }}>Зарегистрироваться</Text>
        </Text>
      </Link>
    </Screen>
  );
}
