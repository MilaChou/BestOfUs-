import { type Href, router, Stack, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Empty, ErrorText, IconButton, Loading } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { localDay, relativeDay } from '@/lib/dates';
import type { AppNotification } from '@/lib/types';

/** Where tapping a notification takes you. */
function target(data: AppNotification['data']): Href | null {
  if (data.task_id) return { pathname: '/task', params: { id: String(data.task_id) } };
  if (data.memory_id) return { pathname: '/memory/[id]', params: { id: String(data.memory_id) } };
  if (data.idea_id) return '/ideas';
  if (data.wish_id) return '/partner';
  switch (data.screen) {
    case 'wishlist_partner':
      return '/partner';
    case 'couple':
      return '/';
    case 'suggest':
      return '/suggest';
    case 'tasks':
      return '/plans';
    case 'on_this_day':
      return '/memories';
    case 'test_partner':
      return {
        pathname: '/test-result',
        params: { test: String(data.test ?? 'love'), whose: 'partner' },
      };
    case 'love_language_partner': // notifications sent before the tests were reworked
      return { pathname: '/test-result', params: { test: 'love', whose: 'partner' } };
    default:
      return null;
  }
}

export default function NotificationsScreen() {
  const [items, setItems] = useState<AppNotification[] | null>(null);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      setItems(await api<AppNotification[]>('/notifications'));
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

  async function open(n: AppNotification) {
    if (!n.is_read) {
      setItems((list) => list?.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)) ?? null);
      api(`/notifications/${n.id}/read`, { method: 'POST' }).catch(() => {});
    }
    const href = target(n.data);
    if (href) router.push(href);
  }

  async function readAll() {
    await api('/notifications/read-all', { method: 'POST' }).catch(() => {});
    setItems((list) => list?.map((x) => ({ ...x, is_read: true })) ?? null);
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Stack.Screen
        options={{
          headerRight: () => (
            <IconButton name="checkmark-done-outline" label="Прочитать все" onPress={readAll} />
          ),
        }}
      />
      {items === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={items ?? []}
          keyExtractor={(n) => String(n.id)}
          contentContainerStyle={{ paddingVertical: space.sm }}
          ListHeaderComponent={error ? <View style={{ padding: space.md }}><ErrorText>{error}</ErrorText></View> : undefined}
          ListEmptyComponent={
            <View style={{ padding: space.md }}>
              <Empty>Пока тихо. Здесь появится, когда партнёр что-то добавит, и напоминания о важных датах.</Empty>
            </View>
          }
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              tintColor={colors.black}
              onRefresh={async () => {
                setRefreshing(true);
                await load();
                setRefreshing(false);
              }}
            />
          }
          renderItem={({ item }) => (
            <Pressable
              onPress={() => open(item)}
              style={({ pressed }) => [styles.row, pressed && { backgroundColor: colors.surface }]}>
              <View style={[styles.dot, item.is_read && { backgroundColor: 'transparent' }]} />
              <View style={{ flex: 1, gap: 2 }}>
                <Text style={[styles.title, !item.is_read && { fontWeight: '700' }]}>{item.title}</Text>
                <Text style={styles.body}>{item.body}</Text>
              </View>
              <Text style={styles.time}>{relativeDay(localDay(item.created_at))}</Text>
            </Pressable>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'flex-start', gap: space.sm, padding: space.md },
  separator: { height: 1, backgroundColor: colors.border, marginLeft: space.md + 16 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.heart, marginTop: 7 },
  title: { fontSize: 15, fontWeight: '500', color: colors.text },
  body: { fontSize: 14, color: colors.muted, lineHeight: 19 },
  time: { fontSize: 12, color: colors.muted },
});
