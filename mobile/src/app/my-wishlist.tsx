import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, FlatList, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Empty, ErrorText, Fab, Loading, Subtitle } from '@/components/ui';
import { WishCard } from '@/components/wish-card';
import { api, errorMessage } from '@/lib/api';
import type { Wish } from '@/lib/types';

/** My own wishlist: what I'd like to receive. The partner sees it in my profile. */
export default function MyWishlistScreen() {
  const [wishes, setWishes] = useState<Wish[] | null>(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      setWishes(await api<Wish[]>('/wishlist/me'));
      setError('');
    } catch (e) {
      setError(errorMessage(e));
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function toggleReceived(wish: Wish) {
    try {
      await api(`/wishlist/me/${wish.id}/received`, { method: wish.is_received ? 'DELETE' : 'POST' });
      await load();
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      {wishes === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={wishes ?? []}
          keyExtractor={(w) => String(w.id)}
          contentContainerStyle={{ padding: space.md, paddingBottom: 100, gap: space.sm }}
          ListHeaderComponent={
            <View style={{ marginBottom: space.sm }}>
              <Subtitle>Партнёр видит этот список в вашем профиле. Что из него решат подарить — вы не узнаете.</Subtitle>
              <ErrorText>{error}</ErrorText>
            </View>
          }
          ListEmptyComponent={<Empty>Пока пусто. Добавьте, что хотели бы получить, кнопкой «+».</Empty>}
          renderItem={({ item }) => (
            <WishCard
              wish={item}
              mine
              onPress={() => router.push({ pathname: '/wish', params: { id: String(item.id) } })}
              onToggleReceived={() => toggleReceived(item)}
            />
          )}
        />
      )}
      <Fab label="Добавить желание" onPress={() => router.push('/wish')} />
    </View>
  );
}
