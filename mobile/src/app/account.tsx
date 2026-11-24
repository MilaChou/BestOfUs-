import { Alert } from 'react-native';

import { useAuth, usePartner } from '@/auth/auth-context';
import { Card, Row, Screen, SectionTitle, Subtitle } from '@/components/ui';
import { api, errorMessage, SERVER_URL } from '@/lib/api';

/** Account settings: who I'm signed in as, sign out, leave the couple. */
export default function AccountScreen() {
  const { user, signOut, refresh } = useAuth();
  const partner = usePartner();

  function confirmSignOut() {
    Alert.alert('Выйти из аккаунта?', 'Всё сохранится — просто войдите снова с тем же email.', [
      { text: 'Отмена', style: 'cancel' },
      { text: 'Выйти', onPress: signOut },
    ]);
  }

  function confirmLeave() {
    Alert.alert(
      'Выйти из пары?',
      partner
        ? 'Общие идеи, планы и воспоминания останутся у партнёра. Это нельзя отменить.'
        : 'Пара и всё, что в ней было, удалится. Это нельзя отменить.',
      [
        { text: 'Отмена', style: 'cancel' },
        {
          text: 'Выйти из пары',
          style: 'destructive',
          onPress: async () => {
            try {
              await api('/couple/leave', { method: 'POST' });
              await refresh();
            } catch (e) {
              Alert.alert('Не получилось', errorMessage(e));
            }
          },
        },
      ],
    );
  }

  return (
    <Screen topInset={false}>
      <SectionTitle>Вы вошли как</SectionTitle>
      <Card>
        <Subtitle>{user?.email}</Subtitle>
      </Card>

      <Card style={{ padding: 0 }}>
        <Row icon="log-out-outline" title="Выйти из аккаунта" onPress={confirmSignOut} />
      </Card>

      <SectionTitle>Пара</SectionTitle>
      <Card style={{ padding: 0 }}>
        <Row icon="exit-outline" title="Выйти из пары" onPress={confirmLeave} danger />
      </Card>

      <Subtitle>Сервер: {SERVER_URL}</Subtitle>
    </Screen>
  );
}
