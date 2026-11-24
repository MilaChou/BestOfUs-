import { useState } from 'react';

import { useAuth } from '@/auth/auth-context';
import { Button, Card, ErrorText, Heading, Input, Screen, Subtitle, Title } from '@/components/ui';
import { api, ApiError, errorMessage } from '@/lib/api';

export default function CoupleScreen() {
  const { user, refresh, signOut } = useAuth();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState<'create' | 'join' | null>(null);

  async function create() {
    setError('');
    setBusy('create');
    try {
      await api('/couple', { method: 'POST', json: {} });
      await refresh(); // the root layout now shows the main screens
    } catch (e) {
      setError(errorMessage(e));
      setBusy(null);
    }
  }

  async function join() {
    setError('');
    setBusy('join');
    try {
      await api('/couple/join', { method: 'POST', json: { invite_code: code } });
      await refresh();
    } catch (e) {
      setError(e instanceof ApiError && e.status === 404 ? 'Такого кода нет — проверьте его' : errorMessage(e));
      setBusy(null);
    }
  }

  return (
    <Screen>
      <Title>Привет, {user?.profile.name}</Title>
      <Subtitle>Чтобы начать, создайте пару или присоединитесь к партнёру по коду.</Subtitle>

      <Card>
        <Heading>Создать пару</Heading>
        <Subtitle>Вы получите код, который нужно отправить партнёру.</Subtitle>
        <Button title="Создать" onPress={create} loading={busy === 'create'} disabled={!!busy} />
      </Card>

      <Card>
        <Heading>У меня есть код</Heading>
        <Input
          value={code}
          onChangeText={setCode}
          placeholder="Например, 87S3UMJW"
          autoCapitalize="characters"
          autoCorrect={false}
        />
        <Button
          title="Присоединиться"
          onPress={join}
          loading={busy === 'join'}
          disabled={!!busy || !code.trim()}
        />
      </Card>

      <ErrorText>{error}</ErrorText>
      <Button title="Выйти из аккаунта" variant="ghost" onPress={signOut} />
    </Screen>
  );
}
