import { Link } from 'expo-router';
import { useState } from 'react';
import { Text } from 'react-native';

import { useAuth } from '@/auth/auth-context';
import { colors } from '@/components/theme';
import { Button, ErrorText, Input, Screen, Subtitle, Title } from '@/components/ui';
import { ApiError, errorMessage } from '@/lib/api';

export default function RegisterScreen() {
  const { signUp } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError('');
    if (password.length < 8) {
      setError('Пароль — минимум 8 символов');
      return;
    }
    setLoading(true);
    try {
      await signUp(email, password, name);
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 409
          ? 'Этот email уже зарегистрирован'
          : e instanceof ApiError && e.status === 422
            ? 'Проверьте email'
            : errorMessage(e),
      );
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Title>Регистрация</Title>
      <Subtitle>Остальное о себе расскажете потом, в профиле</Subtitle>
      <Input label="Как вас зовут" value={name} onChangeText={setName} placeholder="Мила" />
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
        autoComplete="new-password"
        placeholder="Минимум 8 символов"
        onSubmitEditing={submit}
      />
      <ErrorText>{error}</ErrorText>
      <Button
        title="Создать аккаунт"
        onPress={submit}
        loading={loading}
        disabled={!name.trim() || !email || !password}
      />
      <Link href="/login" style={{ textAlign: 'center', padding: 8 }}>
        <Text style={{ color: colors.text, fontSize: 15 }}>
          Уже есть аккаунт? <Text style={{ fontWeight: '600', textDecorationLine: 'underline' }}>Войти</Text>
        </Text>
      </Link>
    </Screen>
  );
}
