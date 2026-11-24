import { router, Stack, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';

import { usePartner } from '@/auth/auth-context';
import { ProfileDetails } from '@/components/profile-details';
import { TestRows } from '@/components/test-rows';
import { colors } from '@/components/theme';
import { Button, Card, Empty, Row, Screen, SectionTitle, Subtitle } from '@/components/ui';
import { WishCard } from '@/components/wish-card';
import { api, errorMessage } from '@/lib/api';
import { daysUntilYearly, formatDate, inDays } from '@/lib/dates';
import type { Wish } from '@/lib/types';

/** Everything about the partner: profile, love language and their wishlist. */
export default function PartnerScreen() {
  const partner = usePartner();
  const [wishes, setWishes] = useState<Wish[] | null>(null);

  const loadWishes = useCallback(async () => {
    try {
      setWishes(await api<Wish[]>('/wishlist/partner'));
    } catch {
      setWishes([]);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadWishes();
    }, [loadWishes]),
  );

  if (!partner) {
    return (
      <Screen topInset={false}>
        <Empty>Партнёр ещё не присоединился.</Empty>
      </Screen>
    );
  }

  const p = partner.profile;

  async function toggleReserve(wish: Wish) {
    try {
      await api(`/wishlist/partner/${wish.id}/reserve`, { method: wish.is_reserved ? 'DELETE' : 'POST' });
      await loadWishes();
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  return (
    <Screen topInset={false}>
      <Stack.Screen options={{ title: '' }} />

      <View style={{ gap: 4 }}>
        <Text style={styles.name}>{p.name}</Text>
        {p.pet_name ? <Subtitle>{p.pet_name}</Subtitle> : null}
        {p.birth_date ? (
          <Subtitle>
            День рождения {formatDate(p.birth_date, false)} — {inDays(daysUntilYearly(p.birth_date))}
          </Subtitle>
        ) : null}
      </View>

      <SectionTitle>Тесты</SectionTitle>
      <TestRows whose="partner" />

      <ProfileDetails profile={p} emptyText="Профиль пока не заполнен." />

      <SectionTitle>Вишлист</SectionTitle>
      <Subtitle>Нажмите «Я подарю» — {p.name} этого не увидит.</Subtitle>
      {wishes?.length ? (
        wishes.map((w) => <WishCard key={w.id} wish={w} mine={false} onToggleReserve={() => toggleReserve(w)} />)
      ) : wishes ? (
        <Empty>Вишлист пока пуст.</Empty>
      ) : null}

      <Button title="Что подарить?" icon="sparkles-outline" onPress={() => router.push('/gift-suggest')} />
      <Card style={{ padding: 0 }}>
        <Row
          icon="lock-closed-outline"
          title="Мои секретные заметки"
          subtitle="Идеи подарков, которые видите только вы"
          onPress={() => router.push('/gift-notes')}
        />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  name: { fontSize: 28, fontWeight: '700', color: colors.text },
});
