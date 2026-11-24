import { router, Stack, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '@/auth/auth-context';
import { ProfileDetails } from '@/components/profile-details';
import { TestRows } from '@/components/test-rows';
import { colors } from '@/components/theme';
import { Button, Empty, IconButton, Screen, SectionTitle, Subtitle } from '@/components/ui';
import { WishCard } from '@/components/wish-card';
import { api, errorMessage } from '@/lib/api';
import { formatDate } from '@/lib/dates';
import type { Wish } from '@/lib/types';

/** My own profile — the same view the partner sees, plus editing and my wishlist. */
export default function MeScreen() {
  const { user } = useAuth();
  const [wishes, setWishes] = useState<Wish[] | null>(null);

  const loadWishes = useCallback(async () => {
    try {
      setWishes(await api<Wish[]>('/wishlist/me'));
    } catch {
      setWishes([]);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadWishes();
    }, [loadWishes]),
  );

  if (!user) return null;
  const p = user.profile;

  async function toggleReceived(wish: Wish) {
    try {
      await api(`/wishlist/me/${wish.id}/received`, { method: wish.is_received ? 'DELETE' : 'POST' });
      await loadWishes();
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  return (
    <Screen topInset={false}>
      <Stack.Screen
        options={{
          title: '',
          headerRight: () => (
            <IconButton name="create-outline" label="Изменить профиль" onPress={() => router.push('/profile')} />
          ),
        }}
      />

      <View style={{ gap: 4 }}>
        <Text style={styles.name}>{p.name}</Text>
        {p.pet_name ? <Subtitle>{p.pet_name}</Subtitle> : null}
        {p.birth_date ? <Subtitle>День рождения {formatDate(p.birth_date)}</Subtitle> : null}
      </View>

      <SectionTitle>Тесты</SectionTitle>
      <TestRows whose="me" />

      <ProfileDetails
        profile={p}
        emptyText="Расскажите о себе: размеры, любимое, как вас поддержать — партнёру будет проще заботиться о вас."
      />
      <Button title="Изменить профиль" icon="create-outline" variant="secondary" onPress={() => router.push('/profile')} />

      <SectionTitle>Мой вишлист</SectionTitle>
      <Subtitle>Партнёр видит этот список. Что из него решат подарить — вы не узнаете.</Subtitle>
      {wishes?.length ? (
        wishes.map((w) => (
          <WishCard
            key={w.id}
            wish={w}
            mine
            onPress={() => router.push({ pathname: '/wish', params: { id: String(w.id) } })}
            onToggleReceived={() => toggleReceived(w)}
          />
        ))
      ) : wishes ? (
        <Empty>Пока пусто.</Empty>
      ) : null}
      <Button title="Добавить желание" icon="add" onPress={() => router.push('/wish')} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  name: { fontSize: 28, fontWeight: '700', color: colors.text },
});

